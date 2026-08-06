"""Placeholder connectors — implement before flipping meta.connector.enabled."""

from __future__ import annotations

from typing import Any


def _todo(name: str):
    def fetch(meta: dict[str, Any]) -> dict:
        raise NotImplementedError(f"Connector {name} is not implemented yet for {meta.get('slug')}")

    return fetch
