from __future__ import annotations
import json
import logging

from dotenv import load_dotenv

load_dotenv()  # reads .env into os.environ before app/session/etc import env vars

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from app.models import FrameMessage
from app.session import Session
from app.groq_client import ai_enabled
from app.supabase_client import enabled as supabase_enabled
from app import reports

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("roadwatch")

app = FastAPI(title="Roadwatch")
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get("/")
async def index(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


@app.get("/api/config")
async def config():
    return {"ai_enabled": ai_enabled(), "supabase_enabled": supabase_enabled()}


# ---------- dashboard / report endpoints (read from Supabase) ----------

@app.get("/api/violations/today")
async def violations_today():
    return await reports.today_violations()


@app.get("/api/violations/monthly")
async def violations_monthly(year: int, month: int):
    return await reports.monthly_report(year, month)


@app.get("/api/violations/common")
async def violations_common(limit: int = 5):
    return await reports.most_common(limit)


@app.get("/api/violations/search")
async def violations_search(
    violation_type: str | None = None,
    vehicle_type: str | None = None,
    zone_name: str | None = None,
    status: str | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 200,
):
    return await reports.search(
        violation_type=violation_type,
        vehicle_type=vehicle_type,
        zone_name=zone_name,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=limit,
    )


@app.websocket("/ws/track")
async def ws_track(ws: WebSocket):
    """One WebSocket connection == one camera feed/session. Client sends a
    JSON 'frame' message (base64 jpeg + current zones/settings) roughly every
    `detect_interval_ms`; server responds with detections/tracks/violations."""
    await ws.accept()
    session = Session()
    try:
        while True:
            raw = await ws.receive_text()
            try:
                payload = json.loads(raw)
            except json.JSONDecodeError:
                continue

            msg_type = payload.get("type")
            if msg_type == "frame":
                try:
                    msg = FrameMessage(**payload)
                except ValidationError as e:
                    await ws.send_json({"type": "error", "error": str(e)})
                    continue
                try:
                    result = await session.process_frame(msg)
                except Exception as e:  # noqa: BLE001
                    log.exception("frame processing failed")
                    await ws.send_json({"type": "error", "error": str(e)})
                    continue
                await ws.send_text(result.model_dump_json())
            elif msg_type == "reset":
                session = Session()
                await ws.send_json({"type": "reset_ok"})
            # unknown message types are ignored
    except WebSocketDisconnect:
        log.info("client disconnected")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)