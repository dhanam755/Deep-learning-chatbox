from __future__ import annotations

from flask import Blueprint, render_template
from flask_login import login_required, current_user

from database.mongo import get_user_by_id, list_chats
from services.auth_service import get_current_user_profile


chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/chat")
@login_required
def dashboard():
    chats = list_chats(current_user.id)
    user_doc = get_current_user_profile(current_user.id) or get_user_by_id(current_user.id)
    active_chat = chats[0] if chats else None
    return render_template("chat.html", chats=chats, user=user_doc, active_chat=active_chat)


@chat_bp.route("/settings")
@login_required
def settings():
    user_doc = get_current_user_profile(current_user.id) or get_user_by_id(current_user.id)
    return render_template("settings.html", user=user_doc)
