from __future__ import annotations
import json
import os
import httpx

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"


def api_key() -> str | None:
    return os.environ.get("GROQ_API_KEY") or None


def ai_enabled() -> bool:
    return bool(api_key())


async def call_groq(data_url: str, prompt_text: str, max_tokens: int = 250) -> dict:
    """Returns {"ok": True, "data": {...parsed json...}} or {"ok": False, "error": str}."""
    key = api_key()
    if not key:
        return {"ok": False, "error": "No GROQ_API_KEY configured on the server."}

    payload = {
        "model": GROQ_MODEL,
        "max_completion_tokens": max_tokens,
        "response_format": {"type": "json_object"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    }
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {key}"}

    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(GROQ_URL, headers=headers, json=payload)
        if resp.status_code != 200:
            return {"ok": False, "error": f"HTTP {resp.status_code}: {resp.text[:150]}"}
        data = resp.json()
        text = data["choices"][0]["message"]["content"]
        text = text.replace("```json", "").replace("```", "").strip()
        return {"ok": True, "data": json.loads(text)}
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "error": str(e) or "network error"}


async def review_violation(snapshot: str, vtype: str, zone_name: str, speed_kmh, limit, vehicle_type: str) -> dict:
    prompt = (
        f'You are an automated traffic-violation reviewer. A computer-vision system flagged a '
        f'vehicle for a possible "{vtype}" violation near {zone_name}. '
    )
    if speed_kmh:
        prompt += f"Estimated speed: {speed_kmh:.1f} km/h in a {limit} km/h zone. "
    prompt += (
        f"Vehicle type: {vehicle_type}. Look at the attached cropped frame and judge whether this "
        'looks like a genuine, clearly-evidenced violation worth sending to a human officer, or a '
        'false positive. Respond with ONLY raw JSON, no markdown: '
        '{"verdict":"confirmed" or "dismissed","reasoning":"<one short sentence>"}'
    )
    return await call_groq(snapshot, prompt, max_tokens=250)


async def inspect_motorcycle(snapshot: str) -> dict:
    prompt = (
        "You are inspecting a cropped traffic-camera frame of a motorcycle. Count how many people "
        "are on it in total (including the driver), and whether each visible rider is wearing a "
        "helmet. Respond with ONLY raw JSON, no markdown: "
        '{"riders":<int>,"all_wearing_helmets":<bool>,"reasoning":"<one short sentence>"}'
    )
    return await call_groq(snapshot, prompt, max_tokens=250)
