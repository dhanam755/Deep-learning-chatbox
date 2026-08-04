from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, session, url_for
from flask_login import current_user, login_required, login_user, logout_user

from extensions import limiter
from services.auth_service import login_user as authenticate_user
from services.auth_service import register_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def root():
    if current_user.is_authenticated:
        return redirect(url_for("chat.dashboard"))
    return redirect(url_for("auth.login"))


@auth_bp.route("/signup", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def signup():
    if current_user.is_authenticated:
        return redirect(url_for("chat.dashboard"))

    if request.method == "POST":
        name = request.form.get("name", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if password != confirm_password:
            flash("Passwords do not match.", "danger")
            return render_template("signup.html")

        created, message = register_user(name, email, password)
        if not created:
            flash(message, "danger")
            return render_template("signup.html")

        flash(message, "success")
        return redirect(url_for("auth.login"))

    return render_template("signup.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per minute")
def register():
    return signup()


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("15 per minute")
def login():
    if current_user.is_authenticated:
        return redirect(url_for("chat.dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        user = authenticate_user(email, password)
        if not user:
            flash("Invalid email or password, or the database is temporarily unavailable.", "danger")
            return render_template("login.html")

        session.permanent = True
        login_user(user)
        return redirect(url_for("chat.dashboard"))

    return render_template("login.html")


@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()
    session.clear()
    flash("You have been signed out.", "success")
    return redirect(url_for("auth.login"))
