import os
import random
import re
from typing import Any

from openai import OpenAI

from personas import Persona, get_persona

ICEBREAKERS = [
    "What's the best meal you've had recently?",
    "If you could teleport anywhere for a first date, where would you go?",
    "What's something you're weirdly passionate about?",
    "Beach day or mountain hike — what's your vibe?",
    "What's a small thing that always makes your day better?",
    "If your life had a theme song right now, what would it be?",
    "What's the most spontaneous thing you've done this year?",
    "Coffee, tea, or something else entirely?",
    "What's a hobby you'd love to try but haven't yet?",
    "Tell me your hottest take — I'll go first if you want 😄",
]

FALLBACK_RESPONSES = {
    "greeting": [
        "Hey! Glad you matched — how's your day going?",
        "Hi there! I was hoping we'd chat. What's on your mind?",
        "Hey! Love that you reached out. What should I know about you?",
    ],
    "question": [
        "That's a great question — I'd say it depends on the mood, but I'm usually up for an adventure.",
        "Hmm, good one. I think about that more than I probably should!",
        "Honestly? I'd have to show you rather than tell you 😊",
    ],
    "compliment": [
        "That's really sweet of you to say — you're making me smile.",
        "Aww, thank you! You're pretty charming yourself.",
        "Okay, you're officially good at this 😄",
    ],
    "default": [
        "Tell me more — I'm curious what made you think of that.",
        "I like where this is going. What else is on your mind?",
        "Ha, fair point. So what do you usually do for fun?",
        "That's interesting! I'd love to hear more about that.",
        "Okay I need details — that sounds like a story.",
    ],
}


def _classify_message(message: str) -> str:
    text = message.lower().strip()
    if re.search(r"\b(hi|hey|hello|howdy|sup)\b", text):
        return "greeting"
    if "?" in text:
        return "question"
    if re.search(r"\b(cute|beautiful|handsome|pretty|gorgeous|hot|attractive)\b", text):
        return "compliment"
    return "default"


def fallback_reply(persona: Persona, user_message: str) -> str:
    category = _classify_message(user_message)
    pool = FALLBACK_RESPONSES.get(category, FALLBACK_RESPONSES["default"])
    base = random.choice(pool)

    interest = random.choice(persona.interests)
    if category == "default" and random.random() < 0.4:
        return f"{base} I'm really into {interest} lately."
    return base


def build_messages(
    persona: Persona, history: list[dict[str, str]], user_message: str
) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [{"role": "system", "content": persona.system_prompt}]
    for turn in history[-12:]:
        messages.append({"role": turn["role"], "content": turn["content"]})
    messages.append({"role": "user", "content": user_message})
    return messages


def generate_reply(
    persona_id: str,
    user_message: str,
    history: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    persona = get_persona(persona_id)
    if not persona:
        raise ValueError(f"Unknown persona: {persona_id}")

    history = history or []
    api_key = os.getenv("OPENAI_API_KEY")

    if api_key:
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=build_messages(persona, history, user_message),
            max_tokens=150,
            temperature=0.85,
        )
        reply = response.choices[0].message.content.strip()
        source = "openai"
    else:
        reply = fallback_reply(persona, user_message)
        source = "fallback"

    return {
        "reply": reply,
        "persona_id": persona.id,
        "source": source,
    }


def get_icebreakers(count: int = 5) -> list[str]:
    return random.sample(ICEBREAKERS, min(count, len(ICEBREAKERS)))
