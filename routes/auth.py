"""
routes/auth.py
---------------
Login, registratie, uitloggen, en profielbeheer. Gemigreerd vanuit de
sqlite3-versie (app.py + validators.py uit hello_flask) naar SQLAlchemy.
"""

import re
from flask import Blueprint, render_template, request, redirect, url_for, session, g
from extensions import db, limiter
from models import User
from utils.auth import login_required

auth_bp = Blueprint("auth", __name__)

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


def is_valid_email(email):
    return bool(EMAIL_PATTERN.match(email or ""))


def is_valid_password(password):
    """Minimaal 8 tekens, met minstens 1 cijfer en 1 speciaal teken."""
    if len(password) < 8:
        return False
    if not any(char.isdigit() for char in password):
        return False
    if not any(char in "!@#$%^&*()-_=+[]{}|;:'\",.<>?/" for char in password):
        return False
    return True


@auth_bp.route("/login", methods=["GET", "POST"])
@limiter.limit("5 per minute")
def login():
    if "user_id" in session:
        return redirect(url_for("main.home"))

    if request.method == "POST":
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()

        error = None
        if not username or not password:
            error = "Gebruikersnaam en wachtwoord zijn verplicht."
        else:
            user = User.query.filter_by(username=username).first()
            if user is None or not user.check_password(password):
                error = "Ongeldige gebruikersnaam of wachtwoord."

        if error:
            return render_template("login.html", error=error)

        session["user_id"] = user.user_id
        return redirect(url_for("main.home"))

    return render_template("login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
@limiter.limit("10 per hour", methods=["POST"])
def register():
    if "user_id" in session:
        return redirect(url_for("main.home"))

    gegevens = {"firstname": "", "lastname": "", "email": "", "username": ""}

    if request.method == "POST":
        firstname = (request.form.get("firstname") or "").strip()
        lastname = (request.form.get("lastname") or "").strip()
        email = (request.form.get("email") or "").strip()
        username = (request.form.get("username") or "").strip()
        password = (request.form.get("password") or "").strip()
        confirm_password = (request.form.get("confirm_password") or "").strip()

        gegevens = {"firstname": firstname, "lastname": lastname, "email": email, "username": username}

        error = None
        if not all([firstname, lastname, username, email, password, confirm_password]):
            error = "Alle velden zijn verplicht."
        elif not is_valid_email(email):
            error = "Ongeldig email formaat."
        elif not is_valid_password(password):
            error = "Wachtwoord moet minimaal 8 tekens, 1 cijfer en 1 speciaal teken bevatten."
        elif password != confirm_password:
            error = "Wachtwoorden komen niet overeen."
        elif User.query.filter_by(username=username).first() is not None:
            error = "Gebruikersnaam bestaat al."
        elif User.query.filter_by(email=email).first() is not None:
            error = "Emailadres is al geregistreerd."

        if error:
            return render_template("register.html", error=error, gegevens=gegevens)

        user = User(first_name=firstname, last_name=lastname, username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return redirect(url_for("auth.login"))

    return render_template("register.html", gegevens=gegevens)


@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))


@auth_bp.route("/profile")
@login_required
def profile():
    prev_orders = (
        g.user.orders and
        sorted(g.user.orders, key=lambda o: o.created_at, reverse=True)[:3]
    )
    return render_template("profile.html", user=g.user, prev_orders=prev_orders)


@auth_bp.route("/update_profile", methods=["POST"])
@login_required
def update_profile():
    firstname = (request.form.get("first_name") or "").strip()
    lastname = (request.form.get("last_name") or "").strip()
    email = (request.form.get("email") or "").strip()
    password = (request.form.get("password") or "").strip()

    errors = []
    if email:
        if not is_valid_email(email):
            errors.append("Ongeldig email formaat.")
        existing = User.query.filter(User.email == email, User.user_id != g.user.user_id).first()
        if existing is not None:
            errors.append("Emailadres is al in gebruik door een andere gebruiker.")

    if password and not is_valid_password(password):
        errors.append("Wachtwoord moet minimaal 8 tekens, 1 cijfer en 1 speciaal teken bevatten.")

    if errors:
        return render_template("profile.html", user=g.user, error=" ".join(errors))

    if firstname:
        g.user.first_name = firstname
    if lastname:
        g.user.last_name = lastname
    if email:
        g.user.email = email
    if password:
        g.user.set_password(password)

    db.session.commit()
    return redirect(url_for("auth.profile"))


@auth_bp.route("/account_settings", methods=["GET"])
@login_required
def account_settings():
    return render_template("account_settings.html", user=g.user)


@auth_bp.route("/delete_account", methods=["POST"])
@login_required
def delete_account():
    db.session.delete(g.user)
    db.session.commit()
    session.clear()
    return redirect(url_for("auth.login"))
