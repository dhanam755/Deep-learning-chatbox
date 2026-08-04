from __future__ import annotations

import json
import re
from io import BytesIO
from typing import List

from flask import Blueprint, Response, jsonify, request, send_file, stream_with_context
from flask_login import current_user, login_required
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

from database.mongo import (
    add_message,
    create_chat,
    delete_chat,
    delete_message,
    get_chat,
    get_recent_user_messages,
    list_chats,
    list_messages,
    serialize_chat,
    update_chat_title,
)
from services.groq_service import AVAILABLE_MODELS, generate_chat_title, get_groq_response, stream_groq_response
from utils.helpers import build_export_txt, normalize_model_name


api_bp = Blueprint("api", __name__)


def safe_filename(value: str, extension: str) -> str:
    filename = re.sub(r"[^a-zA-Z0-9._-]+", "-", value.strip()).strip("-")
    return f"{filename or 'chat'}.{extension}"


@api_bp.route("/models")
@login_required
def models():
    return jsonify({"models": AVAILABLE_MODELS, "default_model": AVAILABLE_MODELS[1]})


@api_bp.route("/chats", methods=["GET"])
@login_required
def chats():
    query = request.args.get("q", "")
    return jsonify({"chats": list_chats(current_user.id, query)})


@api_bp.route("/chats", methods=["POST"])
@login_required
def create_new_chat():
    payload = request.get_json(force=True, silent=True) or {}
    title = (payload.get("title") or "New Chat").strip()[:80] or "New Chat"
    model = normalize_model_name(payload.get("model", ""))
    chat_id = create_chat(current_user.id, title, model)
    return jsonify({"chat_id": chat_id, "title": title, "model": model}), 201


@api_bp.route("/chats/<chat_id>", methods=["GET"])
@login_required
def chat_detail(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    return jsonify({"chat": serialize_chat(chat), "messages": list_messages(chat_id)})


@api_bp.route("/chats/<chat_id>", methods=["PATCH"])
@login_required
def rename_chat(chat_id: str):
    payload = request.get_json(force=True, silent=True) or {}
    title = (payload.get("title") or "").strip()[:80]
    if not title:
        return jsonify({"error": "Title is required."}), 400
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    update_chat_title(chat_id, title)
    return jsonify({"message": "Chat renamed.", "title": title})


@api_bp.route("/chats/<chat_id>", methods=["DELETE"])
@login_required
def remove_chat(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    delete_chat(chat_id, current_user.id)
    return jsonify({"message": "Chat deleted."})


@api_bp.route("/chat", methods=["POST"])
@login_required
def chat():
    payload = request.get_json(force=True, silent=True) or {}
    message = (payload.get("message") or "").strip()
    chat_id = payload.get("chat_id")
    model = normalize_model_name(payload.get("model", ""))

    if not message:
        return jsonify({"error": "Message is required."}), 400

    is_new_chat = not chat_id
    generated_title = ""
    if is_new_chat:
        generated_title = generate_chat_title(message, model)
        chat_id = create_chat(current_user.id, generated_title, model)
    else:
        chat = get_chat(chat_id, current_user.id)
        if not chat:
            return jsonify({"error": "Chat not found."}), 404
        model = normalize_model_name(chat.get("model", model))
        generated_title = chat.get("title", "New Chat")

    add_message(chat_id, "user", message)
    history = get_recent_user_messages(chat_id, limit=10)
    assistant_text = get_groq_response(message, model=model, history=history[:-1])
    add_message(chat_id, "assistant", assistant_text)

    if is_new_chat or len(list_messages(chat_id)) <= 2:
        update_chat_title(chat_id, generated_title)

    return jsonify({"chat_id": chat_id, "response": assistant_text, "title": generated_title})


@api_bp.route("/chat/stream", methods=["POST"])
@login_required
def chat_stream():
    payload = request.get_json(force=True, silent=True) or {}
    message = (payload.get("message") or "").strip()
    chat_id = payload.get("chat_id")
    model = normalize_model_name(payload.get("model", ""))

    if not message:
        return jsonify({"error": "Message is required."}), 400

    is_new_chat = not chat_id
    generated_title = ""
    if is_new_chat:
        generated_title = generate_chat_title(message, model)
        chat_id = create_chat(current_user.id, generated_title, model)
    else:
        chat = get_chat(chat_id, current_user.id)
        if not chat:
            return jsonify({"error": "Chat not found."}), 404
        model = normalize_model_name(chat.get("model", model))
        generated_title = chat.get("title", "New Chat")

    add_message(chat_id, "user", message)
    history = get_recent_user_messages(chat_id, limit=10)

    def event_stream():
        try:
            chunks: List[str] = []
            yield f"event: meta\ndata: {json.dumps({'chat_id': chat_id, 'model': model})}\n\n"
            for chunk in stream_groq_response(message, model=model, history=history[:-1]):
                chunks.append(chunk)
                yield f"data: {json.dumps({'chunk': chunk})}\n\n"
            final_text = "".join(chunks).strip() or get_groq_response(message, model=model, history=history[:-1])
            add_message(chat_id, "assistant", final_text)
            if is_new_chat or len(list_messages(chat_id)) <= 2:
                update_chat_title(chat_id, generated_title)
            yield f"event: done\ndata: {json.dumps({'chat_id': chat_id, 'response': final_text})}\n\n"
        except Exception as exc:
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"

    return Response(
        stream_with_context(event_stream()),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@api_bp.route("/chats/<chat_id>/regenerate", methods=["POST"])
@login_required
def regenerate(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404

    model = normalize_model_name(chat.get("model", ""))
    messages_for_chat = list_messages(chat_id)
    last_assistant_index = next((index for index in range(len(messages_for_chat) - 1, -1, -1) if messages_for_chat[index].get("role") == "assistant"), None)
    if last_assistant_index is None:
        return jsonify({"error": "No assistant response found to regenerate."}), 400

    last_user_index = next((index for index in range(last_assistant_index - 1, -1, -1) if messages_for_chat[index].get("role") == "user"), None)
    if last_user_index is None:
        return jsonify({"error": "No user message found to regenerate."}), 400

    delete_message(messages_for_chat[last_assistant_index]["id"], chat_id)
    history = messages_for_chat[:last_user_index][-10:]
    assistant_text = get_groq_response(messages_for_chat[last_user_index].get("content", ""), model=model, history=history)
    add_message(chat_id, "assistant", assistant_text)
    return jsonify({"chat_id": chat_id, "response": assistant_text})


@api_bp.route("/messages/<chat_id>", methods=["GET"])
@login_required
def messages(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    return jsonify({"messages": list_messages(chat_id)})


@api_bp.route("/export/<chat_id>.txt", methods=["GET"])
@login_required
def export_txt(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404
    messages = list_messages(chat_id)
    payload = build_export_txt(chat.get("title", "Chat"), messages)
    filename = safe_filename(chat.get("title", "chat"), "txt")
    return Response(payload, mimetype="text/plain", headers={"Content-Disposition": f'attachment; filename="{filename}"'})


@api_bp.route("/export/<chat_id>.pdf", methods=["GET"])
@login_required
def export_pdf(chat_id: str):
    chat = get_chat(chat_id, current_user.id)
    if not chat:
        return jsonify({"error": "Chat not found."}), 404

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    _, height = letter
    y = height - 40
    pdf.setTitle(chat.get("title", "Chat"))
    pdf.drawString(40, y, chat.get("title", "Chat"))
    y -= 30

    for message in list_messages(chat_id):
        text = f"{message['role'].title()}: {message['content']}"
        for line in text.splitlines() or [text]:
            if y < 50:
                pdf.showPage()
                y = height - 40
            pdf.drawString(40, y, line[:110])
            y -= 16
        y -= 8

    pdf.save()
    buffer.seek(0)
    filename = safe_filename(chat.get("title", "chat"), "pdf")
    return send_file(buffer, mimetype="application/pdf", as_attachment=True, download_name=filename)
