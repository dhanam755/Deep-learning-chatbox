from __future__ import annotations

from typing import Generator, List, Optional

from groq import Groq

from config import Config
from database.mongo import summarize_title


client = Groq(api_key=Config.GROQ_API_KEY) if Config.GROQ_API_KEY else None
DEFAULT_MODEL = "llama-3.1-8b-instant"
AVAILABLE_MODELS = [
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
]


def _build_messages(prompt: str, history: Optional[List[dict]] = None) -> List[dict]:
    messages = [
        {
            "role": "system",
            "content": (
                "You are a production-grade ChatGPT-style assistant. "
                "Answer clearly, safely, and with concise but useful structure when helpful."
            ),
        }
    ]
    if history:
        for item in history:
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": prompt})
    return messages


def _fallback_response(prompt: str) -> str:
    return (
        "Groq API key is not configured. "
        "Set GROQ_API_KEY in your environment to enable AI responses. "
        f"Your message was: {prompt}"
    )


def stream_groq_response(prompt: str, model: str = DEFAULT_MODEL, history: Optional[List[dict]] = None) -> Generator[str, None, str]:
    if client is None:
        yield _fallback_response(prompt)
        return _fallback_response(prompt)

    try:
        stream = client.chat.completions.create(
            model=model if model in AVAILABLE_MODELS else DEFAULT_MODEL,
            messages=_build_messages(prompt, history),
            temperature=0.7,
            max_tokens=1200,
            stream=True,
        )

        collected: List[str] = []
        for chunk in stream:
            delta = chunk.choices[0].delta.content if chunk.choices else None
            if delta:
                collected.append(delta)
                yield delta
        return "".join(collected)
    except Exception as exc:
        message = f"AI service error: {exc}"
        yield message
        return message


def get_groq_response(prompt: str, model: str = DEFAULT_MODEL, history: Optional[List[dict]] = None) -> str:
    if client is None:
        return _fallback_response(prompt)

    try:
        completion = client.chat.completions.create(
            model=model if model in AVAILABLE_MODELS else DEFAULT_MODEL,
            messages=_build_messages(prompt, history),
            temperature=0.7,
            max_tokens=1200,
        )
        return completion.choices[0].message.content or ""
    except Exception as exc:
        return f"AI service error: {exc}"


def generate_chat_title(prompt: str, model: str = DEFAULT_MODEL) -> str:
    if client is None:
        return summarize_title(prompt)

    try:
        completion = client.chat.completions.create(
            model=model if model in AVAILABLE_MODELS else DEFAULT_MODEL,
            messages=[
                {"role": "system", "content": "Generate a short descriptive chat title in 6 words or fewer. Return only the title."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=20,
        )
        title = completion.choices[0].message.content or ""
        title = title.strip().strip('"')
        return title if title else summarize_title(prompt)
    except Exception:
        return summarize_title(prompt)
