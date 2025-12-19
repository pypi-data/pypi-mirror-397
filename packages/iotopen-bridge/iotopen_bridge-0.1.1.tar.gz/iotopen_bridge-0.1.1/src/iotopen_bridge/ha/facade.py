# SPDX-License-Identifier: Apache-2.0
# File: src/iotopen_bridge/ha/facade.py
from __future__ import annotations

import asyncio
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any, Protocol

from ..bridge.config import BridgeConfig
from ..bridge.runtime import BridgeRuntime


class _HassLike(Protocol):
    """The small subset of Home Assistant we need.

    We intentionally use a Protocol to avoid a hard dependency on Home Assistant.
    """

    loop: asyncio.AbstractEventLoop

    def async_add_executor_job(self, func: Any, *args: Any) -> asyncio.Future:  # type: ignore[override]
        ...


def build_bridge_config(
    *,
    # Lynx / IoT Open
    base_url: str,
    api_key: str,
    installation_id: int | str,
    # MQTT
    mqtt_host: str,
    mqtt_port: int = 1883,
    mqtt_username: str | None = None,
    mqtt_password: str | None = None,
    mqtt_client_id: str | None = None,
    mqtt_tls: bool = False,
    mqtt_tls_insecure: bool = False,
    mqtt_tls_cafile: str | None = None,
    # HA Discovery
    discovery_prefix: str = "homeassistant",
    object_id_prefix: str = "iotopen",
    node_id: str | None = None,
    # Storage & operational knobs
    storage_path: str = "./state/iotopen-bridge.sqlite3",
    log_level: str = "INFO",
    authz_mode: str = "disabled",
) -> BridgeConfig:
    """Build a validated BridgeConfig from simple parameters.

    This is meant for Home Assistant config flows: you already have these values and
    don't want to write/parse YAML in your custom component.

    All additional bridge features are still accessible via BridgeConfig fields.
    """
    data: dict[str, Any] = {
        "lynx": {
            "base_url": base_url,
            "api_key": api_key,
            "installation_id": int(installation_id),
        },
        "mqtt": {
            "host": mqtt_host,
            "port": int(mqtt_port),
        },
        "ha": {
            "node_id": node_id or str(installation_id),
            "object_id_prefix": object_id_prefix,
            "discovery": {"prefix": discovery_prefix},
        },
        "authz": {"mode": authz_mode},
        "storage_path": storage_path,
        "log_level": log_level,
    }

    if mqtt_username:
        data["mqtt"]["username"] = mqtt_username
    if mqtt_password:
        data["mqtt"]["password"] = mqtt_password
    if mqtt_client_id:
        data["mqtt"]["client_id"] = mqtt_client_id

    if mqtt_tls:
        data["mqtt"]["tls"] = {
            "enabled": True,
            "insecure": bool(mqtt_tls_insecure),
        }
        if mqtt_tls_cafile:
            data["mqtt"]["tls"]["cafile"] = mqtt_tls_cafile

    cfg = BridgeConfig.from_mapping(data)
    cfg.validate()
    return cfg


@dataclass
class HABridgeHandle:
    """A minimal async-friendly wrapper around BridgeRuntime for Home Assistant."""

    runtime: BridgeRuntime

    @classmethod
    def from_config(cls, cfg: BridgeConfig) -> HABridgeHandle:
        return cls(runtime=BridgeRuntime(cfg))

    @classmethod
    def from_mapping(cls, data: Mapping[str, Any]) -> HABridgeHandle:
        cfg = BridgeConfig.from_mapping(dict(data))
        cfg.validate()
        return cls.from_config(cfg)

    async def async_start(self, hass: _HassLike) -> None:
        # BridgeRuntime.start() is blocking for a short time and creates background threads.
        await hass.async_add_executor_job(self.runtime.start)

    async def async_stop(self, hass: _HassLike) -> None:
        await hass.async_add_executor_job(self.runtime.stop)

    async def async_inventory_refresh(self, hass: _HassLike) -> None:
        # InventoryController is owned by runtime; expose the safe entrypoint if present.
        fn = getattr(self.runtime, "_safe_inventory_refresh", None)
        if fn is None:
            return
        await hass.async_add_executor_job(fn)

    async def async_publish_discovery(self, hass: _HassLike) -> None:
        pub = getattr(self.runtime, "discovery", None)
        if pub is None:
            return
        fn = getattr(pub, "publish_all", None)
        if fn is None:
            return
        await hass.async_add_executor_job(fn)
