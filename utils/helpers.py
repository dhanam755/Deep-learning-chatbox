from __future__ import annotations

import html
import re
from typing import Any, Dict, Iterable, List

from markupsafe import Markup


ALLOWED_MODEL_NAMES = {
    "llama-3.3-70b-versatile",
    "llama-3.1-8b-instant",
    "gemma2-9b-it",
}


def safe_text(value: str) -> str:
    return html.escape(value or "").strip()


def normalize_model_name(model: str) -> str:
    model = (model or "").strip()
    return model if model in ALLOWED_MODEL_NAMES else "llama-3.1-8b-instant"


def extract_plain_text_from_markdown(markdown_text: str) -> str:
    text = markdown_text or ""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"[#>*_~]", "", text)
    return text.strip()


def build_export_txt(title: str, messages: List[Dict[str, Any]]) -> str:
    lines = [title, "=" * len(title), ""]
    for message in messages:
        speaker = message.get("role", "assistant").title()
        content = message.get("content", "")
        lines.append(f"{speaker}: {content}")
        lines.append("")
    return "\n".join(lines).strip() + "\n"


def build_export_pdf_fallback(title: str, messages: List[Dict[str, Any]]) -> str:
    return build_export_txt(title, messages)
