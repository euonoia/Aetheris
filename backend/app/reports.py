from __future__ import annotations
from datetime import datetime, timezone
from collections import Counter

from . import supabase_client as sb


async def today_violations() -> list[dict]:
    start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    return await sb.select(
        "violations",
        [
            ("select", "*"),
            ("occurred_at", f"gte.{start.isoformat()}"),
            ("order", "occurred_at.desc"),
        ],
    )


async def monthly_report(year: int, month: int) -> list[dict]:
    start = datetime(year, month, 1, tzinfo=timezone.utc)
    end_year, end_month = (year + 1, 1) if month == 12 else (year, month + 1)
    end = datetime(end_year, end_month, 1, tzinfo=timezone.utc)
    return await sb.select(
        "violations",
        [
            ("select", "*"),
            ("occurred_at", f"gte.{start.isoformat()}"),
            ("occurred_at", f"lt.{end.isoformat()}"),
            ("order", "occurred_at.desc"),
        ],
    )


async def most_common(limit: int = 5) -> list[dict]:
    """Aggregation done in Python since we're on the REST API rather than a
    direct SQL connection. Fine at this data volume; move to an RPC/SQL view
    (e.g. `select violation_type, count(*) from violations group by 1`) if the
    table grows large."""
    rows = await sb.select("violations", [("select", "violation_type")])
    counts = Counter(r["violation_type"] for r in rows if r.get("violation_type"))
    return [{"violation_type": vt, "count": c} for vt, c in counts.most_common(limit)]


async def search(
    violation_type: str | None = None,
    vehicle_type: str | None = None,
    zone_name: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 200,
) -> list[dict]:
    params: list[tuple[str, str]] = [
        ("select", "*"),
        ("order", "occurred_at.desc"),
        ("limit", str(limit)),
    ]
    if violation_type:
        params.append(("violation_type", f"eq.{violation_type}"))
    if vehicle_type:
        params.append(("vehicle_type", f"eq.{vehicle_type}"))
    if zone_name:
        params.append(("zone_name", f"ilike.*{zone_name}*"))
    if status:
        params.append(("ai_review_status", f"eq.{status}"))
    if date_from:
        params.append(("occurred_at", f"gte.{date_from}"))
    if date_to:
        params.append(("occurred_at", f"lte.{date_to}"))
    return await sb.select("violations", params)