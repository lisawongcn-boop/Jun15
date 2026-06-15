import os
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from bot import generate_reply, get_icebreakers
from personas import PERSONAS

load_dotenv()

ROOT = Path(__file__).resolve().parent.parent
FRONTEND_DIR = ROOT / "frontend"

app = FastAPI(title="Dating Chat Bot", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    persona_id: str
    message: str = Field(min_length=1, max_length=1000)
    history: list[ChatMessage] = Field(default_factory=list)


class ChatResponse(BaseModel):
    reply: str
    persona_id: str
    source: str


@app.get("/api/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/api/personas")
def list_personas() -> list[dict]:
    return [
        {
            "id": p.id,
            "name": p.name,
            "age": p.age,
            "tagline": p.tagline,
            "bio": p.bio,
            "interests": p.interests,
            "avatar_color": p.avatar_color,
        }
        for p in PERSONAS
    ]


@app.get("/api/icebreakers")
def icebreakers(count: int = 5) -> dict[str, list[str]]:
    return {"icebreakers": get_icebreakers(count)}


@app.post("/api/chat", response_model=ChatResponse)
def chat(request: ChatRequest) -> ChatResponse:
    try:
        history = [{"role": m.role, "content": m.content} for m in request.history]
        result = generate_reply(request.persona_id, request.message, history)
        return ChatResponse(**result)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail="Failed to generate reply") from exc


@app.get("/")
def serve_index() -> FileResponse:
    return FileResponse(FRONTEND_DIR / "index.html")


app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")
