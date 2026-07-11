from __future__ import annotations
import os
import httpx

# Read from environment only -- never hardcode keys here.
# Set these in a local .env / your shell / your host's env-var settings:
#   SUPABASE_URL=https://xxxxxxxx.supabase.co
#   SUPABASE_KEY=<publishable/anon key>   (NOT the service_role key)
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")


def enabled() -> bool:
    return bool(SUPABASE_URL and SUPABASE_KEY)


def _headers(prefer: str | None = None) -> dict:
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def _rest_url(table: str) -> str:
    return f"{SUPABASE_URL}/rest/v1/{table}"


async def insert(table: str, row: dict) -> dict | None:
    """Inserts one row, returns the inserted row (with generated id) or None
    if Supabase isn't configured. Raises on error so callers can decide how
    to handle a failed write (we don't want a DB outage to crash detection)."""
    if not enabled():
        return None
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            _rest_url(table), headers=_headers(prefer="return=representation"), json=row
        )
    if resp.status_code >= 300:
        raise RuntimeError(f"Supabase insert into {table} failed: {resp.status_code} {resp.text[:300]}")
    data = resp.json()
    return data[0] if isinstance(data, list) and data else None


async def patch(table: str, match: dict, updates: dict) -> None:
    """Updates row(s) matching an equality filter, e.g. match={'id': '...'}"""
    if not enabled():
        return
    params = [(k, f"eq.{v}") for k, v in match.items()]
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.patch(_rest_url(table), headers=_headers(), params=params, json=updates)
    if resp.status_code >= 300:
        raise RuntimeError(f"Supabase patch on {table} failed: {resp.status_code} {resp.text[:300]}")


async def select(table: str, params: list[tuple[str, str]]) -> list[dict]:
    """params is a list of (key, value) tuples so PostgREST filters that repeat
    a column (e.g. two occurred_at range bounds) work correctly."""
    if not enabled():
        return []
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(_rest_url(table), headers=_headers(), params=params)
    if resp.status_code >= 300:
        raise RuntimeError(f"Supabase select on {table} failed: {resp.status_code} {resp.text[:300]}")
    return resp.json()