# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/bridge/runtime.py
from __future__ import annotations

import inspect
import logging
import threading
import time
from collections.abc import Callable
from contextlib import suppress
from dataclasses import dataclass, field
from typing import Any

from ..adapters.ha_discovery_publisher import HADiscoveryPublisher
from ..adapters.mqtt_router import MqttRouter
from ..adapters.raw_capture import RawCapture
from ..bridge.config import BridgeConfig
from ..bridge.health import Health
from ..bridge.health_http import HealthServer
from ..controllers.commands import CommandsController
from ..controllers.inventory import InventoryController
from ..controllers.telemetry import TelemetryController
from ..core.event_bus import EventBus
from ..core.registry import Registry
from ..lynx.auth import LynxAuth
from ..lynx.client import LynxApiClient
from ..observability.metrics import Metrics
from ..security.authz.from_config import build_policy_bundle_from_bridge_config
from ..security.authz.policy import PolicyEngine
from ..security.authz.rules import AuthzRules
from ..security.tls.profiles import TLSSettings
from ..storage.cache import CachedStore
from ..storage.sqlite_store import SQLiteStore
from ..transport.mqtt.paho_client import PahoMqttClient, PahoMqttConfig

_LOGGER = logging.getLogger(__name__)


def _init_signature_params(cls_or_fn: Any) -> tuple[set[str], bool]:
    target = cls_or_fn
    if inspect.isclass(cls_or_fn):
        target = cls_or_fn.__init__

    try:
        sig = inspect.signature(target)
    except (TypeError, ValueError):
        return set(), True

    names: set[str] = set()
    has_var_kwargs = False
    for name, p in sig.parameters.items():
        if name == "self":
            continue
        if p.kind == inspect.Parameter.VAR_KEYWORD:
            has_var_kwargs = True
            continue
        names.add(name)
    return names, has_var_kwargs


def _construct_flex(cls: type[Any], *, label: str, candidates: dict[str, Any]) -> Any:
    names, has_var_kwargs = _init_signature_params(cls)

    if has_var_kwargs or not names:
        try:
            return cls(**candidates)
        except TypeError as e:
            raise TypeError(
                f"{label}: failed constructing {cls.__name__} with provided candidates"
            ) from e

    filtered = {k: v for k, v in candidates.items() if k in names}

    try:
        return cls(**filtered)
    except TypeError as e:
        raise TypeError(
            f"{label}: failed constructing {cls.__name__}. "
            f"Allowed params={sorted(names)} provided={sorted(filtered.keys())}"
        ) from e


def _build_lynx_auth(*, base_url: str, api_key: str) -> LynxAuth:
    api_key_s = str(api_key)
    base_url_s = str(base_url)

    init_params, has_var_kwargs = _init_signature_params(LynxAuth)

    def _try(*args: Any, **kwargs: Any) -> LynxAuth:
        return LynxAuth(*args, **kwargs)

    attempts: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

    if has_var_kwargs or "base_url_or_api_key" in init_params:
        attempts.append(((), {"base_url_or_api_key": base_url_s, "api_key": api_key_s}))
        attempts.append(((), {"base_url_or_api_key": api_key_s}))
        attempts.append(((), {"base_url_or_api_key": base_url_s}))

    if has_var_kwargs or ("base_url" in init_params and "api_key" in init_params):
        attempts.append(((), {"base_url": base_url_s, "api_key": api_key_s}))

    if has_var_kwargs or "api_key" in init_params:
        attempts.append(((), {"api_key": api_key_s}))

    attempts.append(((api_key_s,), {}))
    attempts.append(((base_url_s, api_key_s), {}))
    attempts.append(((base_url_s,), {}))

    last_type_error: TypeError | None = None
    for args, kwargs in attempts:
        try:
            return _try(*args, **kwargs)
        except TypeError as e:
            last_type_error = e

    raise TypeError(
        "Unable to construct LynxAuth with supported patterns. "
        "Check src/iotopen_bridge/lynx/auth.py __init__ signature."
    ) from last_type_error


def _norm_topic(s: str | None) -> str:
    t = str(s or "").strip()
    if t.startswith("/"):
        t = t[1:]
    return t


def _unwrap_health_server(hs: Any) -> Any:
    """Try to find the underlying HTTPServer/TCPServer object that exposes .server_address."""
    if hs is None:
        return None
    if hasattr(hs, "server_address"):
        return hs

    for name in (
        "_srv",
        "srv",
        "_server",
        "server",
        "_httpd",
        "httpd",
        "_http_server",
        "http_server",
    ):
        inner = getattr(hs, name, None)
        if inner is not None and hasattr(inner, "server_address"):
            return inner

    host = getattr(hs, "host", None)
    port = getattr(hs, "port", None)
    if isinstance(host, str) and isinstance(port, int) and port != 0:

        class _Shim:
            server_address = (host, port)

        return _Shim()

    return hs


@dataclass
class BridgeRuntime:
    cfg: BridgeConfig
    metrics: Metrics = field(default_factory=Metrics)
    mqtt_client: Any | None = None

    _stop: threading.Event = field(default_factory=threading.Event, init=False)
    _threads: list[threading.Thread] = field(default_factory=list, init=False)

    bus: EventBus = field(init=False)
    registry: Registry = field(init=False)
    store: CachedStore = field(init=False)
    api: LynxApiClient = field(init=False)

    mqtt: Any = field(init=False)

    discovery: HADiscoveryPublisher = field(init=False)
    telemetry: TelemetryController = field(init=False)
    commands: CommandsController = field(init=False)
    inventory: InventoryController = field(init=False)
    router: MqttRouter = field(init=False)

    policy_rules: AuthzRules = field(init=False)
    policy: PolicyEngine = field(init=False)

    bridge_availability_topic: str = field(init=False)

    health_http: HealthServer | None = field(default=None, init=False)
    _health_srv: Any = field(default=None, init=False)

    health: Health = field(default_factory=Health, init=False)

    _upstream_subscribed: set[str] = field(default_factory=set, init=False)
    _ha_cmd_subscribed: set[str] = field(default_factory=set, init=False)

    def __post_init__(self) -> None:
        self.bus = EventBus()
        self.registry = Registry()

        sqlite = SQLiteStore(path=self.cfg.storage_path)
        self.store = CachedStore(store=sqlite)

        auth = _build_lynx_auth(base_url=self.cfg.lynx.base_url, api_key=self.cfg.lynx.api_key)
        self.api = LynxApiClient(base_url=self.cfg.lynx.base_url, auth=auth)

        bundle = build_policy_bundle_from_bridge_config(self.cfg)
        self.policy_rules = bundle.rules
        self.policy = bundle.policy

        self.bridge_availability_topic = f"{self.cfg.ha.state_prefix}/bridge/availability"

        if self.mqtt_client is not None:
            self.mqtt = self.mqtt_client
        else:
            mqtt_cfg = PahoMqttConfig(
                host=self.cfg.mqtt.host,
                port=int(self.cfg.mqtt.port),
                username=self.cfg.mqtt.username,
                password=self.cfg.mqtt.password,
                client_id=self.cfg.mqtt.client_id,
                keepalive=int(self.cfg.mqtt.keepalive),
                tls=TLSSettings.from_any(self.cfg.mqtt.tls),
                will_topic=self.bridge_availability_topic,
                will_payload="offline",
                will_qos=1,
                will_retain=True,
            )
            raw_capture = RawCapture(self.cfg.raw_capture)
            self.mqtt = PahoMqttClient(cfg=mqtt_cfg, raw_capture=raw_capture, policy=self.policy)

        pub = getattr(self.mqtt, "publish", None)
        if not callable(pub):
            raise TypeError("MQTT client missing callable publish(topic, payload, qos, retain)")

        self.discovery = _construct_flex(
            HADiscoveryPublisher,
            label="discovery",
            candidates={
                "registry": self.registry,
                "store": self.store,
                "discovery_prefix": self.cfg.ha.discovery.prefix,
                "state_prefix": self.cfg.ha.state_prefix,
                "publish": pub,
                "publisher": pub,
                "mqtt_publish": pub,
                "bridge_availability_topic": self.bridge_availability_topic,
                "attributes_enabled": bool(self.cfg.ha.publish_attributes),
                "per_entity_availability": bool(self.cfg.ha.availability.per_entity_enabled),
            },
        )

        self.telemetry = _construct_flex(
            TelemetryController,
            label="telemetry",
            candidates={
                "registry": self.registry,
                "ha": self.discovery,
                "discovery": self.discovery,
                "publisher": self.discovery,
            },
        )

        self.commands = _construct_flex(
            CommandsController,
            label="commands",
            candidates={
                "bus": self.bus,
                "event_bus": self.bus,
                "registry": self.registry,
                "mqtt_publish": pub,
                "publish": pub,
                "publisher": pub,
                "policy": self.policy,
                "policy_engine": self.policy,
                "authz": self.policy,
            },
        )

        self.inventory = InventoryController(
            api=self.api,
            registry=self.registry,
            bus=self.bus,
            store=self.store,
            installation_id=int(self.cfg.lynx.installation_id),
            policy_rules=self.policy_rules,
            authz_cfg=self.cfg.authz,
        )

        self.router = MqttRouter(
            telemetry=self.telemetry,
            commands=self.commands,
            state_prefix=self.cfg.ha.state_prefix,
        )

        if hasattr(self.mqtt, "set_on_message"):
            self.mqtt.set_on_message(self._on_message_mux)
        if hasattr(self.mqtt, "set_on_connect"):
            self.mqtt.set_on_connect(self._on_connect)
        if hasattr(self.mqtt, "set_on_disconnect"):
            self.mqtt.set_on_disconnect(self._on_disconnect)

        from ..models.events import InventoryEvent

        self.bus.subscribe(InventoryEvent, self._on_inventory_event)

        if getattr(self.cfg.health_http, "enabled", False):
            self.health_http = HealthServer(
                host=str(self.cfg.health_http.host),
                port=int(self.cfg.health_http.port),
                status_fn=self._health_status,
                metrics_fn=getattr(self.metrics, "render_prometheus", None),
            )

    # --- rest unchanged ---
    def start(self) -> None:
        if self.health_http:
            with suppress(Exception):
                self.health_http.start()
            self._health_srv = _unwrap_health_server(self.health_http)

        with suppress(Exception):
            self.mqtt.connect()

        self._start_thread("inventory-refresh", self._inventory_refresh_loop)
        self._start_thread("availability-watchdog", self._availability_watchdog_loop)

        with suppress(Exception):
            self._safe_inventory_refresh()

    def run_forever(self) -> None:
        """Block until stopped (CTRL+C safe)."""
        try:
            while not self._stop.is_set():
                time.sleep(0.25)
        except KeyboardInterrupt:
            _LOGGER.info("KeyboardInterrupt: stopping")
        finally:
            self.stop()

    def run(self) -> int:
        _LOGGER.info("Starting IoT Open Bridge runtime")
        self.start()
        self.run_forever()
        return 0

    def stop(self) -> None:
        if self._stop.is_set():
            return
        self._stop.set()

        with suppress(Exception):
            self.discovery.publish_bridge_availability(False)

        with suppress(Exception):
            self.mqtt.disconnect()

        if self.health_http:
            with suppress(Exception):
                self.health_http.stop()

        for t in self._threads:
            with suppress(Exception):
                t.join(timeout=3)

        with suppress(Exception):
            self.api.close()

        _LOGGER.info("Stopped")

    def _safe_inventory_refresh(self) -> None:
        try:
            self.inventory.refresh_sync()
            self.health.set_inventory_ok(True, timestamp=time.time())
            self.health.set_error(None)
        except Exception as e:
            self.health.set_inventory_ok(False, timestamp=time.time())
            self.health.set_error(str(e))
            _LOGGER.debug("Safe inventory refresh failed", exc_info=True)

    def _on_message_mux(self, topic: str, payload: bytes, qos: int, retain: bool) -> None:
        with suppress(Exception):
            fn = getattr(self.metrics, "on_mqtt_message", None)
            if callable(fn):
                fn(topic=str(topic))
            else:
                fn2 = getattr(self.metrics, "mqtt_on_message", None)
                if callable(fn2):
                    fn2(str(topic))

        self.router.on_message(str(topic), bytes(payload), int(qos), bool(retain))

    def _on_connect(self, ok: bool, msg: str) -> None:
        _LOGGER.info("MQTT connect ok=%s msg=%s", ok, msg)
        self.health.set_connected(ok)

        if not ok:
            return

        with suppress(Exception):
            self.discovery.publish_bridge_availability(True)

        # ✅ Commands: support both legacy (<iid>/<fid>/set) AND extended (<iid>/<fid>/<kind>/set)
        sp = str(self.cfg.ha.state_prefix).strip("/")
        with suppress(Exception):
            self.mqtt.subscribe(f"{sp}/+/+/set", qos=1)
        with suppress(Exception):
            self.mqtt.subscribe(f"{sp}/+/+/+/set", qos=1)

        with suppress(Exception):
            self._sync_upstream_subscriptions()
            self._sync_ha_command_subscriptions()

    def _on_disconnect(self, rc: int, msg: str) -> None:
        _LOGGER.warning("MQTT disconnect rc=%s msg=%s", rc, msg)
        self.health.set_connected(False)

        with suppress(Exception):
            self.discovery.publish_bridge_availability(False)

    def _on_inventory_event(self, ev: Any) -> None:
        if getattr(ev, "removed_functions", None):
            with suppress(Exception):
                self.discovery.garbage_collect(ev.removed_functions)

        with suppress(Exception):
            self.discovery.publish_all()

        with suppress(Exception):
            self._sync_upstream_subscriptions()
            self._sync_ha_command_subscriptions()

    def _sync_upstream_subscriptions(self) -> None:
        want: set[str] = set()
        for fx in self.registry.iter_functions():
            tr = _norm_topic(getattr(fx, "topic_read", None))
            if tr:
                want.add(tr)

        add = want - self._upstream_subscribed
        rem = self._upstream_subscribed - want

        for t in sorted(rem):
            with suppress(Exception):
                self.mqtt.unsubscribe(t)

        for t in sorted(add):
            with suppress(Exception):
                self.mqtt.subscribe(t, qos=1)

        self._upstream_subscribed = want

    def _sync_ha_command_subscriptions(self) -> None:
        # Keep per-entity legacy topic subscriptions as before (still useful for fine-grained broker ACL setups).
        want: set[str] = set()
        sp = str(self.cfg.ha.state_prefix).strip("/")
        for fx in self.registry.iter_functions():
            iid = int(getattr(fx, "installation_id", 0) or 0)
            fid = int(getattr(fx, "function_id", 0) or 0)
            if iid and fid:
                want.add(f"{sp}/{iid}/{fid}/set")

        add = want - self._ha_cmd_subscribed
        rem = self._ha_cmd_subscribed - want

        for t in sorted(rem):
            with suppress(Exception):
                self.mqtt.unsubscribe(t)

        for t in sorted(add):
            with suppress(Exception):
                self.mqtt.subscribe(t, qos=1)

        self._ha_cmd_subscribed = want

    def _inventory_refresh_loop(self) -> None:
        interval = max(5, int(self.cfg.scheduler.inventory_refresh_seconds))
        while not self._stop.is_set():
            with suppress(Exception):
                self._safe_inventory_refresh()
            self._stop.wait(interval)

    def _availability_watchdog_loop(self) -> None:
        offline_after = max(5, int(self.cfg.ha.availability.offline_after_seconds))
        tick = 2.0

        while not self._stop.is_set():
            now = time.time()
            last_seen_items = list(self.registry.last_seen.items())

            for fid, ts in last_seen_items:
                if (now - float(ts)) >= offline_after:
                    fx = self.registry.get_function(int(fid))
                    if fx is None:
                        continue
                    with suppress(Exception):
                        iid = int(getattr(fx, "installation_id", 0) or 0)
                        self.discovery.publish_entity_availability(iid, int(fid), False)

            self._stop.wait(tick)

    def _start_thread(self, name: str, target: Callable[[], None]) -> None:
        t = threading.Thread(name=f"iotopen-bridge-{name}", target=target, daemon=True)
        self._threads.append(t)
        t.start()

    def _health_status(self) -> dict[str, Any]:
        collisions: list[str] = []
        with suppress(Exception):
            collisions = sorted(self.registry.topic_collisions())

        return {
            "ok": True,
            "mqtt_connected": bool(self.health.mqtt_connected),
            "last_inventory_ok": bool(self.health.last_inventory_ok),
            "last_inventory_ts": self.health.last_inventory_ts,
            "last_error": self.health.last_error,
            "mqtt": {"host": self.cfg.mqtt.host, "port": int(self.cfg.mqtt.port)},
            "lynx": {
                "base_url": self.cfg.lynx.base_url,
                "installation_id": int(self.cfg.lynx.installation_id),
            },
            "inventory": {
                "count": len(list(self.registry.iter_functions())),
                "topic_collisions": collisions,
            },
            "authz": {
                "mode": str(self.cfg.authz.mode),
                "allow_prefixes": len(self.cfg.authz.allow_prefixes),
                "allow_topics": len(self.cfg.authz.allow_topics),
                "deny_prefixes": len(self.cfg.authz.deny_prefixes),
            },
            "time": time.time(),
        }
