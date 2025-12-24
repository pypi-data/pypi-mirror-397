# File: src/iotopen_bridge/adapters/ha_native_publisher.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class NativeStateSnapshot:
    """Immutable read model for a single function."""

    installation_id: int
    function_id: int
    available: bool
    last_seen: float | None
    state: bytes | None
    attributes: dict[str, Any] | None


class NativeStateStore:
    """Thread-safe in-memory HA state store.

    This replaces MQTT state topics when ha.transport="native".
    """

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state: dict[tuple[int, int], bytes] = {}
        self._attrs: dict[tuple[int, int], dict[str, Any]] = {}
        self._avail: dict[tuple[int, int], bool] = {}
        self._seen: dict[tuple[int, int], float] = {}

    def set_available(self, installation_id: int, function_id: int, available: bool) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._avail[key] = bool(available)
            self._seen[key] = time.time()

    def set_state(self, installation_id: int, function_id: int, payload: bytes) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._state[key] = bytes(payload)
            self._seen[key] = time.time()

    def set_attributes(self, installation_id: int, function_id: int, attrs: dict[str, Any]) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._attrs[key] = dict(attrs)
            self._seen[key] = time.time()

    def get_snapshot(self, installation_id: int, function_id: int) -> NativeStateSnapshot:
        key = (int(installation_id), int(function_id))
        with self._lock:
            return NativeStateSnapshot(
                installation_id=key[0],
                function_id=key[1],
                # Default to available=True so entities are usable immediately in native mode
                available=bool(self._avail.get(key, True)),
                last_seen=self._seen.get(key),
                state=self._state.get(key),
                attributes=dict(self._attrs[key]) if key in self._attrs else None,
            )

    def drop_function(self, installation_id: int, function_id: int) -> None:
        key = (int(installation_id), int(function_id))
        with self._lock:
            self._state.pop(key, None)
            self._attrs.pop(key, None)
            self._avail.pop(key, None)
            self._seen.pop(key, None)


@dataclass(frozen=True, slots=True)
class NativePublisherConfig:
    """Config for native mode (no downstream MQTT)."""

    state_prefix: str
    per_entity_availability: bool
    attributes_enabled: bool = True
    bridge_availability_topic: str = ""


class HANativePublisher:
    """Publisher for HA 'native' transport.

    Instead of publishing MQTT state/discovery, we update an in-memory store.
    The HA integration reads snapshots from this store and updates entities.
    """

    def __init__(
        self,
        *,
        store: NativeStateStore,
        state_prefix: str,
        per_entity_availability: bool,
        attributes_enabled: bool = True,
    ) -> None:
        self.store = store
        self.state_prefix = state_prefix
        self.per_entity_availability = bool(per_entity_availability)
        self.attributes_enabled = bool(attributes_enabled)

    # --- availability paths ---
    def publish_bridge_availability(self, online: bool) -> None:
        # In native mode, bridge availability is handled by the HA integration's own coordinator/health.
        return

    def publish_entity_availability(
        self, installation_id: int, function_id: int, online: bool
    ) -> None:
        if not self.per_entity_availability:
            return
        self.store.set_available(int(installation_id), int(function_id), bool(online))

    # --- state/attributes paths ---
    def publish_attributes(
        self,
        installation_id: int,
        function_id: int,
        attrs: dict[str, Any],
        qos: int,
        retain: bool,
    ) -> None:
        if not self.attributes_enabled:
            return
        self.store.set_attributes(int(installation_id), int(function_id), attrs)

    def publish(self, topic: str, payload: Any, qos: int, retain: bool) -> None:
        """Generic publish hook used by controllers.

        We only care about state topics:
            <state_prefix>/<iid>/<fid>/state
        """
        try:
            parts = [p for p in str(topic).strip("/").split("/") if p]
            if len(parts) < 4:
                return
            prefix, iid_s, fid_s, key = parts[0], parts[1], parts[2], parts[3]
            if prefix != str(self.state_prefix).strip("/"):
                return
            if key != "state":
                return
            iid = int(iid_s)
            fid = int(fid_s)
        except Exception:
            return

        # Store state for both str and bytes-like payloads
        b = payload.encode("utf-8") if isinstance(payload, str) else bytes(payload)
        self.store.set_state(iid, fid, b)
