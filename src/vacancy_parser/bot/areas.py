"""Lightweight in-memory cache for hh.ru area dictionary.

The `/areas` endpoint returns a nested tree of countries → regions → cities.
For onboarding we flatten it into (id, name, parent_name) so a user typing
a city name gets a disambiguated list.
"""
from __future__ import annotations

import logging
from typing import Any

import httpx

from vacancy_parser.config import settings

log = logging.getLogger(__name__)

_AREAS_URL = "https://api.hh.ru/areas"

# module-level cache: list of (id, name, parent_name)
_flat_cache: list[tuple[str, str, str | None]] | None = None


def _flatten(nodes: list[dict[str, Any]], parent_name: str | None) -> list[tuple[str, str, str | None]]:
    out: list[tuple[str, str, str | None]] = []
    for node in nodes:
        out.append((node["id"], node["name"], parent_name))
        children = node.get("areas") or []
        if children:
            out.extend(_flatten(children, node["name"]))
    return out


async def _load() -> list[tuple[str, str, str | None]]:
    global _flat_cache
    if _flat_cache is not None:
        return _flat_cache
    async with httpx.AsyncClient(timeout=15.0, headers={"User-Agent": settings.hh_user_agent}) as c:
        resp = await c.get(_AREAS_URL)
        resp.raise_for_status()
        data = resp.json()
    _flat_cache = _flatten(data, None)
    log.info("Loaded %d hh.ru areas into cache", len(_flat_cache))
    return _flat_cache


async def search_areas(query: str, limit: int = 5) -> list[tuple[str, str]]:
    """Return up to `limit` areas whose name starts with (or contains) `query`.

    Result items are (area_id, display_name) where display_name includes the
    parent for disambiguation, e.g. "Москва" or "Красноярск (Красноярский край)".
    """
    q = query.strip().lower()
    if not q:
        return []
    all_areas = await _load()

    starts = []
    contains = []
    for aid, name, parent in all_areas:
        name_l = name.lower()
        display = f"{name} ({parent})" if parent else name
        if name_l == q:
            return [(aid, display)]
        if name_l.startswith(q):
            starts.append((aid, display))
        elif q in name_l:
            contains.append((aid, display))
        if len(starts) >= limit:
            break

    return (starts + contains)[:limit]
