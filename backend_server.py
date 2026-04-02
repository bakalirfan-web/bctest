import json
import os
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8787"))
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")


class Handler(BaseHTTPRequestHandler):
    def _set_headers(self, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", ALLOWED_ORIGIN)
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers(204)

    def do_POST(self):
        if self.path != "/api/telegram":
            self._set_headers(404)
            self.wfile.write(json.dumps({"ok": False, "error": "Not found"}).encode())
            return

        if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
            self._set_headers(500)
            self.wfile.write(json.dumps({"ok": False, "error": "Server secrets missing"}).encode())
            return

        length = int(self.headers.get("Content-Length", "0"))
        raw = self.rfile.read(length)

        try:
            payload = json.loads(raw.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": "Invalid JSON"}).encode())
            return

        message = str(payload.get("message", "")).strip()
        parse_mode = str(payload.get("parse_mode", "HTML"))

        if not message:
            self._set_headers(400)
            self.wfile.write(json.dumps({"ok": False, "error": "Message is required"}).encode())
            return

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

        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                telegram_data = json.loads(resp.read().decode("utf-8"))
            ok = bool(telegram_data.get("ok"))
            self._set_headers(200 if ok else 502)
            self.wfile.write(json.dumps({"ok": ok, "telegram": telegram_data}).encode())
        except urllib.error.HTTPError as e:
            self._set_headers(502)
            self.wfile.write(json.dumps({"ok": False, "error": f"Telegram HTTP {e.code}"}).encode())
        except Exception as e:
            self._set_headers(502)
            self.wfile.write(json.dumps({"ok": False, "error": str(e)}).encode())


if __name__ == "__main__":
    print(f"Backend listening on http://{HOST}:{PORT}")
    print("POST /api/telegram")
    HTTPServer((HOST, PORT), Handler).serve_forever()
