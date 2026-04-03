import json
import os
import urllib.error
import urllib.request

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")


def _json_response(start_response, status, payload):
    body = json.dumps(payload).encode("utf-8")
    headers = [
        ("Content-Type", "application/json"),
        ("Access-Control-Allow-Origin", ALLOWED_ORIGIN),
        ("Access-Control-Allow-Methods", "POST, OPTIONS, GET"),
        ("Access-Control-Allow-Headers", "Content-Type"),
    ]
    start_response(status, headers)
    return [body]


def _send_to_telegram(message, parse_mode):
    body = json.dumps(
        {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message,
            "parse_mode": parse_mode,
        }
    ).encode("utf-8")

    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    req = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode("utf-8"))


def application(environ, start_response):
    method = environ.get("REQUEST_METHOD", "GET")
    path = environ.get("PATH_INFO", "/")

    if method == "OPTIONS":
        return _json_response(start_response, "204 No Content", {"ok": True})

    if method == "GET" and path in ("/", "/health", "/healthz"):
        return _json_response(
            start_response,
            "200 OK",
            {"ok": True, "service": "telegram-backend"},
        )

    if method != "POST" or path != "/api/telegram":
        return _json_response(start_response, "404 Not Found", {"ok": False, "error": "Not found"})

    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return _json_response(
            start_response,
            "500 Internal Server Error",
            {"ok": False, "error": "Server secrets missing"},
        )

    try:
        length = int(environ.get("CONTENT_LENGTH") or 0)
    except ValueError:
        length = 0

    raw = environ.get("wsgi.input").read(length) if length > 0 else b""

    try:
        payload = json.loads(raw.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Invalid JSON"})

    message = str(payload.get("message", "")).strip()
    parse_mode = str(payload.get("parse_mode", "HTML"))

    if not message:
        return _json_response(start_response, "400 Bad Request", {"ok": False, "error": "Message is required"})

    try:
        telegram_data = _send_to_telegram(message, parse_mode)
        ok = bool(telegram_data.get("ok"))
        status = "200 OK" if ok else "502 Bad Gateway"
        return _json_response(start_response, status, {"ok": ok, "telegram": telegram_data})
    except urllib.error.HTTPError as err:
        return _json_response(
            start_response,
            "502 Bad Gateway",
            {"ok": False, "error": f"Telegram HTTP {err.code}"},
        )
    except Exception as err:
        return _json_response(start_response, "502 Bad Gateway", {"ok": False, "error": str(err)})
