from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from database.mongo import chats, messages, users, serialize_chat, serialize_message, serialize_user


OUTPUT_PATH = Path("chat_data.csv")


def iter_export_rows() -> Iterable[dict]:
    for message in messages.find().sort("timestamp", 1):
        chat = chats.find_one({"_id": message.get("chat_id")})
        user = users.find_one({"_id": chat.get("user_id")}) if chat else None
        serialized_chat = serialize_chat(chat) if chat else {}
        serialized_user = serialize_user(user) if user else {}
        serialized_message = serialize_message(message)

        yield {
            "user_name": serialized_user.get("name", ""),
            "user_email": serialized_user.get("email", ""),
            "chat_title": serialized_chat.get("title", ""),
            "chat_model": serialized_chat.get("model", ""),
            "message_role": serialized_message.get("role", ""),
            "message_content": serialized_message.get("content", ""),
            "message_timestamp": serialized_message.get("timestamp", ""),
        }


def export_csv(output_path: Path = OUTPUT_PATH) -> Path:
    rows = list(iter_export_rows())
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()) if rows else [
            "user_name",
            "user_email",
            "chat_title",
            "chat_model",
            "message_role",
            "message_content",
            "message_timestamp",
        ])
        writer.writeheader()
        writer.writerows(rows)
    return output_path


if __name__ == "__main__":
    path = export_csv()
    print(f"Exported chat data to {path.resolve()}")
