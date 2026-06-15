# Spark — Dating App Chat Bot

A dating-style chat bot for practicing conversations. Pick a persona, break the ice, and chat with AI matches that have distinct personalities.

## Features

- **4 AI personas** with unique bios, interests, and conversation styles
- **Dating-app UI** — match screen, chat bubbles, typing indicator, icebreaker chips
- **OpenAI-powered replies** when you set an API key
- **Demo mode fallback** — works out of the box without any API key

## Quick start

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

## Optional: enable smarter AI replies

Copy the example env file and add your OpenAI key:

```bash
cp .env.example .env
# Edit .env and set OPENAI_API_KEY
```

Restart the server. Replies will use `gpt-4o-mini` by default (configurable via `OPENAI_MODEL`).

## API

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/personas` | GET | List available chat personas |
| `/api/chat` | POST | Send a message and get a reply |
| `/api/icebreakers` | GET | Get conversation starter suggestions |
| `/api/health` | GET | Health check |

### Chat request example

```json
{
  "persona_id": "alex",
  "message": "Hey! What's your favorite way to spend a weekend?",
  "history": []
}
```

## Project structure

```
backend/
  main.py        # FastAPI server
  bot.py         # Reply generation (OpenAI + fallback)
  personas.py    # Persona definitions
frontend/
  index.html     # App shell
  styles.css     # Dating-app styling
  app.js         # Chat UI logic
```

## Personas

| Name | Vibe |
|------|------|
| Alex | Warm, curious, outdoorsy |
| Jordan | Witty, intellectual, bookish |
| Sam | Upbeat, adventurous, casual |
| Riley | Thoughtful, creative, gentle |

## License

MIT
