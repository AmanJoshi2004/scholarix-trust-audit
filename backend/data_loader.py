"""
data_loader.py

Loads the provided researcher data (data/authors/<name>/{profile,publications,
broad_impact}.json) into memory once at startup and exposes simple lookup
helpers. Kept intentionally simple: ~50 authors / ~350 broad_impact records
is small enough to hold in memory, no database needed for a prototype.
"""

from __future__ import annotations
import json
import os
from functools import lru_cache

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "authors")


def _slug(folder_name: str) -> str:
    """Use the folder name itself as a stable, URL-safe author id."""
    return folder_name


def _safe_load(path: str):
    if not os.path.exists(path):
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


@lru_cache(maxsize=1)
def load_all_authors() -> dict:
    """Returns {author_id: {"profile": ..., "publications": [...], "broad_impact": [...]}}"""
    authors = {}
    if not os.path.isdir(DATA_DIR):
        return authors

    for entry in sorted(os.listdir(DATA_DIR)):
        folder = os.path.join(DATA_DIR, entry)
        if not os.path.isdir(folder) or entry.startswith("."):
            continue

        profile = _safe_load(os.path.join(folder, "profile.json")) or {}
        publications = _safe_load(os.path.join(folder, "publications.json")) or []
        broad_impact = _safe_load(os.path.join(folder, "broad_impact.json")) or []

        author_id = _slug(entry)
        authors[author_id] = {
            "id": author_id,
            "profile": profile,
            "publications": publications,
            "broad_impact": broad_impact,
        }
    return authors


def get_author(author_id: str) -> dict | None:
    return load_all_authors().get(author_id)


def list_authors() -> list[dict]:
    return list(load_all_authors().values())


def reload_data():
    """Clears the cache -- useful for tests or if data files change on disk."""
    load_all_authors.cache_clear()
