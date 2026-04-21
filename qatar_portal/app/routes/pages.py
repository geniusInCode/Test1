from flask import Blueprint, render_template, session, redirect, url_for

pages_bp = Blueprint("pages", __name__)


@pages_bp.route("/")
def index():
    if "admin_id" in session:
        return redirect(url_for("pages.dashboard"))
    return redirect(url_for("pages.login"))


@pages_bp.route("/signup")
def signup():
    if "admin_id" in session:
        return redirect(url_for("pages.dashboard"))
    return render_template("signup.html")


@pages_bp.route("/login")
def login():
    if "admin_id" in session:
        return redirect(url_for("pages.dashboard"))
    return render_template("login.html")


@pages_bp.route("/forgot-password")
def forgot_password():
    return render_template("forgot_password.html")


@pages_bp.route("/reset-password")
def reset_password():
    return render_template("reset_password.html")


@pages_bp.route("/dashboard")
def dashboard():
    if "admin_id" not in session:
        return redirect(url_for("pages.login"))
    return render_template("dashboard.html")
