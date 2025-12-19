# File: src/iotopen_bridge/observability/tracing.py
# SPDX-License-Identifier: Apache-2.0

"""
OpenTelemetry tracing bootstrap.

Design goals:
- No extra exporter dependencies (only opentelemetry-api + opentelemetry-sdk)
- Optional console exporter for debugging
- Safe to call multiple times

Env:
  - IOTOPEN_BRIDGE_TRACING_ENABLED: 1/true/yes to enable (default: false)
  - IOTOPEN_BRIDGE_TRACING_CONSOLE: 1/true/yes to add ConsoleSpanExporter (default: false)
"""

from __future__ import annotations

import os
from dataclasses import dataclass

from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


def _env_bool(name: str, default: bool = False) -> bool:
    v = (os.environ.get(name) or "").strip().lower()
    if not v:
        return default
    return v in {"1", "true", "t", "yes", "y", "on"}


@dataclass(frozen=True, slots=True)
class TracingConfig:
    enabled: bool = False
    console_exporter: bool = False
    service_name: str = "iotopen-bridge"


def load_tracing_config(service_name: str = "iotopen-bridge") -> TracingConfig:
    return TracingConfig(
        enabled=_env_bool("IOTOPEN_BRIDGE_TRACING_ENABLED", False),
        console_exporter=_env_bool("IOTOPEN_BRIDGE_TRACING_CONSOLE", False),
        service_name=service_name,
    )


def configure_tracing(service_name: str = "iotopen-bridge") -> TracerProvider | None:
    """Configure the global tracer provider. Returns provider if enabled, else None."""
    cfg = load_tracing_config(service_name=service_name)
    if not cfg.enabled:
        return None

    resource = Resource.create({"service.name": cfg.service_name})
    provider = TracerProvider(resource=resource)

    if cfg.console_exporter:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))

    trace.set_tracer_provider(provider)
    return provider


def get_tracer(name: str = "iotopen-bridge"):
    """Return a tracer handle (API-stable helper used by observability.__init__)."""
    return trace.get_tracer(name)
