# File: src/iotopen_bridge/controllers/commands.py
# SPDX-License-Identifier: Apache-2.0
from __future__ import annotations

import contextlib
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from ...converters.mapping.ha_props import infer_semantics
from ...converters.normalize.bool import to_bool
from ...core.errors import PolicyDenied
from ...core.event_bus import EventBus
from ...core.registry import Registry
from ...models.events import CommandEvent
from ...models.lynx import FunctionX
from ...security.authz.policy import PolicyEngine

PublishFn = Callable[[str, str | bytes, int, bool], None]
_LOGGER = logging.getLogger(__name__)

_QOS: int = 1
_RETAIN: bool = False


def _encode_payload(value: Any) -> str | bytes:
    if value is None:
        return ""
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, (str, int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _extract_bool(payload: bytes) -> bool | None:
    s = payload.decode("utf-8", errors="replace").strip()
    b = to_bool(s)
    if b is not None:
        return bool(b)

    if s.startswith("{") and s.endswith("}"):
        try:
            obj = json.loads(s)
        except Exception:
            return None
        if isinstance(obj, dict):
            for key in ("state", "on", "value", "enabled"):
                if key in obj:
                    return to_bool(obj.get(key))
    return None


def _extract_int(payload: bytes) -> int | None:
    s = payload.decode("utf-8", errors="replace").strip()
    try:
        return int(float(s))
    except Exception:
        return None


def _extract_float(payload: bytes) -> float | None:
    s = payload.decode("utf-8", errors="replace").strip()
    try:
        return float(s)
    except Exception:
        return None


def _extract_text(payload: bytes) -> str:
    return payload.decode("utf-8", errors="replace").strip()


def _switch_publish_value(fx: FunctionX, on: bool) -> Any:
    if on:
        return fx.state_on if fx.state_on is not None else "ON"
    return fx.state_off if fx.state_off is not None else "OFF"


@dataclass
class CommandsController:
    registry: Registry
    bus: EventBus
    policy: PolicyEngine
    mqtt_publish: PublishFn

    def _emit(
        self, *, function_id: int, topic: str, value: Any, ok: bool, error: str | None = None
    ) -> None:
        with contextlib.suppress(Exception):
            self.bus.publish(
                CommandEvent(
                    function_id=int(function_id),
                    topic=str(topic or ""),
                    value=value,
                    ok=bool(ok),
                    error=(str(error) if error else None),
                )
            )

    def handle_ha_set(
        self,
        installation_id: int,
        function_id: int,
        payload: bytes,
        *,
        subkey: str | None = None,
    ) -> None:
        """Handle HA command topics:
        - .../set             (base command)
        - .../set/<subkey>    (extended command channel)
        """
        fx = self.registry.get_function(int(function_id))
        if fx is None:
            self._emit(
                function_id=int(function_id),
                topic="",
                value=None,
                ok=False,
                error="unknown function_id",
            )
            return

        fx_iid = int(getattr(fx, "installation_id", 0) or 0)
        if fx_iid and fx_iid != int(installation_id):
            self._emit(
                function_id=int(function_id),
                topic=getattr(fx, "topic_set", "") or "",
                value=None,
                ok=False,
                error="installation_id mismatch",
            )
            return

        if not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=None, ok=False, error="no topic_set"
            )
            return

        sem = infer_semantics(fx)

        # ---- SWITCH ----
        if sem.component == "switch":
            on = _extract_bool(payload)
            if on is None:
                s = _extract_text(payload)
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=s,
                    ok=False,
                    error="invalid bool",
                )
                return
            self.send_switch(int(function_id), on=bool(on))
            return

        # ---- LIGHT ----
        if sem.component == "light":
            if subkey in (None, "state"):
                on = _extract_bool(payload)
                if on is None:
                    s = _extract_text(payload)
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=s,
                        ok=False,
                        error="invalid bool",
                    )
                    return
                self.send_light(int(function_id), on=bool(on))
                return

            if subkey == "brightness":
                bri = _extract_int(payload)
                if bri is None:
                    s = _extract_text(payload)
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=s,
                        ok=False,
                        error="invalid brightness",
                    )
                    return
                self.send_light_brightness(int(function_id), brightness=int(bri))
                return

            if subkey == "color_temp":
                ct = _extract_int(payload)
                if ct is None:
                    s = _extract_text(payload)
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=s,
                        ok=False,
                        error="invalid color_temp",
                    )
                    return
                self.send_light_color_temp(int(function_id), color_temp=int(ct))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported light subkey",
            )
            return

        # ---- COVER ----
        if sem.component == "cover":
            if subkey in (None, "command"):
                cmd = _extract_text(payload).upper()
                if cmd not in ("OPEN", "CLOSE", "STOP"):
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=cmd,
                        ok=False,
                        error="invalid cover cmd",
                    )
                    return
                self.send_cover_command(int(function_id), cmd)
                return

            if subkey == "position":
                pos = _extract_int(payload)
                if pos is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text(payload),
                        ok=False,
                        error="invalid position",
                    )
                    return
                self.send_cover_position(int(function_id), int(pos))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported cover subkey",
            )
            return

        # ---- CLIMATE ----
        if sem.component == "climate":
            if subkey == "mode":
                mode = _extract_text(payload)
                if not mode:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=mode,
                        ok=False,
                        error="empty mode",
                    )
                    return
                self.send_climate_mode(int(function_id), mode)
                return

            if subkey == "temperature":
                temp = _extract_float(payload)
                if temp is None:
                    self._emit(
                        function_id=int(function_id),
                        topic=str(fx.topic_set),
                        value=_extract_text(payload),
                        ok=False,
                        error="invalid temperature",
                    )
                    return
                self.send_climate_temperature(int(function_id), float(temp))
                return

            self._emit(
                function_id=int(function_id),
                topic=str(fx.topic_set),
                value=subkey,
                ok=False,
                error="unsupported climate subkey",
            )
            return

        # ---- NUMBER ----
        if sem.component == "number":
            if subkey not in (None, "value"):
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=subkey,
                    ok=False,
                    error="unsupported number subkey",
                )
                return
            val = _extract_float(payload)
            if val is None:
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=_extract_text(payload),
                    ok=False,
                    error="invalid number",
                )
                return
            self.send_number(int(function_id), float(val))
            return

        # ---- SELECT ----
        if sem.component == "select":
            if subkey not in (None, "option"):
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=subkey,
                    ok=False,
                    error="unsupported select subkey",
                )
                return
            opt = _extract_text(payload)
            if not opt:
                self._emit(
                    function_id=int(function_id),
                    topic=str(fx.topic_set),
                    value=opt,
                    ok=False,
                    error="empty option",
                )
                return
            self.send_select(int(function_id), opt)
            return

        # ---- BUTTON ----
        if sem.component == "button":
            # Any payload triggers; default PRESS in discovery
            self.press_button(int(function_id))
            return

        # fallback
        self._emit(
            function_id=int(function_id),
            topic=str(fx.topic_set),
            value=subkey,
            ok=False,
            error=f"unsupported component {sem.component}",
        )

    # ---------- publish helpers ----------

    def _publish(self, fx: FunctionX, value: Any) -> bool:
        topic = str(fx.topic_set)
        try:
            self.policy.require_publish(topic)
        except PolicyDenied as e:
            self._emit(
                function_id=int(fx.function_id), topic=topic, value=value, ok=False, error=str(e)
            )
            return False

        try:
            self.mqtt_publish(topic, _encode_payload(value), _QOS, _RETAIN)
        except Exception as e:
            _LOGGER.debug("Publish failed function_id=%s topic=%s err=%s", fx.function_id, topic, e)
            self._emit(
                function_id=int(fx.function_id), topic=topic, value=value, ok=False, error=str(e)
            )
            return False

        self._emit(function_id=int(fx.function_id), topic=topic, value=value, ok=True)
        return True

    def send_switch(self, function_id: int, on: bool) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=on, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, _switch_publish_value(fx, on))

    def send_light(self, function_id: int, on: bool) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=on, ok=False, error="no topic_set"
            )
            return
        # if state_on/off exist, honor them; else ON/OFF
        self._publish(fx, _switch_publish_value(fx, on))

    def send_light_brightness(self, function_id: int, brightness: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=brightness,
                ok=False,
                error="no topic_set",
            )
            return
        # generic JSON envelope (device-specific bridges can translate downstream)
        self._publish(fx, {"brightness": int(brightness)})

    def send_light_color_temp(self, function_id: int, color_temp: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=color_temp,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, {"color_temp": int(color_temp)})

    def send_cover_command(self, function_id: int, cmd: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=cmd, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"command": str(cmd)})

    def send_cover_position(self, function_id: int, position: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=position,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, {"position": int(position)})

    def send_climate_mode(self, function_id: int, mode: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=mode, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"mode": str(mode)})

    def send_climate_temperature(self, function_id: int, temperature: float) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value=temperature,
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, {"temperature": float(temperature)})

    def send_number(self, function_id: int, value: float) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=value, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"value": float(value)})

    def send_select(self, function_id: int, option: str) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id), topic="", value=option, ok=False, error="no topic_set"
            )
            return
        self._publish(fx, {"option": str(option)})

    def press_button(self, function_id: int) -> None:
        fx = self.registry.get_function(int(function_id))
        if fx is None or not getattr(fx, "topic_set", None):
            self._emit(
                function_id=int(function_id),
                topic="",
                value="PRESS",
                ok=False,
                error="no topic_set",
            )
            return
        self._publish(fx, {"press": True})
