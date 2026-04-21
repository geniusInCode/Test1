import os
import logging
from datetime import timedelta
from flask import Blueprint, request, jsonify, session, current_app
from app.extensions import db
from app.models.admin import Admin
from app.models.reset_token import PasswordResetToken
from app.utils.validators import validate_signup, validate_login

auth_bp = Blueprint("auth", __name__)
logger  = logging.getLogger(__name__)

RESET_EXPIRY  = int(os.environ.get("RESET_TOKEN_EXPIRY_SECONDS", 3600))
REMEMBER_TTL  = int(os.environ.get("REMEMBER_ME_LIFETIME", 2592000))


# ── US-1.1  SIGN UP ───────────────────────────────────────────────────────────
@auth_bp.route("/signup", methods=["POST"])
def signup():
    data   = request.get_json(silent=True) or {}
    errors = validate_signup(data)
    if errors:
        return jsonify({"success": False, **errors}), 422

    if Admin.query.filter_by(email=data["email"].lower()).first():
        return jsonify({
            "success": False,
            "error":   "An account with this email already exists.",
            "field":   "email"
        }), 409

    admin = Admin(
        full_name=data["full_name"].strip(),
        email=data["email"].lower()
    )
    admin.set_password(data["password"])
    db.session.add(admin)
    db.session.commit()

    logger.info("New admin registered: %s", admin.email)
    return jsonify({
        "success": True,
        "data":    {"message": "Account created successfully. Please log in."}
    }), 201


# ── US-1.2  LOGIN ─────────────────────────────────────────────────────────────
@auth_bp.route("/login", methods=["POST"])
def login():
    data   = request.get_json(silent=True) or {}
    errors = validate_login(data)
    if errors:
        return jsonify({"success": False, **errors}), 422

    admin = Admin.query.filter_by(email=data["email"].lower()).first()
    if not admin or not admin.check_password(data["password"]):
        return jsonify({"success": False, "error": "Invalid email or password."}), 401

    remember_me = bool(data.get("remember_me", False))
    if remember_me:
        session.permanent = True
        current_app.permanent_session_lifetime = timedelta(seconds=REMEMBER_TTL)
    else:
        session.permanent = False

    session["admin_id"]    = admin.id
    session["admin_email"] = admin.email
    session["admin_name"]  = admin.full_name

    logger.info("Admin logged in: %s | remember_me=%s", admin.email, remember_me)
    return jsonify({"success": True, "data": admin.to_dict()}), 200


# ── LOGOUT ────────────────────────────────────────────────────────────────────
@auth_bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True, "data": {"message": "Logged out successfully."}}), 200


# ── US-1.3  FORGOT PASSWORD ───────────────────────────────────────────────────
@auth_bp.route("/forgot-password", methods=["POST"])
def forgot_password():
    data  = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()

    GENERIC_RESPONSE = {
        "success": True,
        "data":    {"message": "If an account with this email exists, a reset link has been generated. Check your server logs."}
    }

    if not email:
        return jsonify(GENERIC_RESPONSE), 200

    admin = Admin.query.filter_by(email=email).first()
    if admin:
        token_obj = PasswordResetToken(admin_id=admin.id)
        db.session.add(token_obj)
        db.session.commit()

        reset_link = f"http://localhost:5000/reset-password?token={token_obj.token}"
        # In production: send email. For now: log it.
        logger.warning("=" * 60)
        logger.warning("RESET LINK (NOT EMAILED — USE THIS IN BROWSER):")
        logger.warning(reset_link)
        logger.warning("=" * 60)
        print(f"\n{'='*60}\nRESET LINK: {reset_link}\n{'='*60}\n")

    return jsonify(GENERIC_RESPONSE), 200


# ── US-1.3  RESET PASSWORD ────────────────────────────────────────────────────
@auth_bp.route("/reset-password", methods=["POST"])
def reset_password():
    data      = request.get_json(silent=True) or {}
    token_str = str(data.get("token", "")).strip()
    new_pass  = str(data.get("password", "")).strip()
    confirm   = str(data.get("confirm_password", "")).strip()

    if not token_str:
        return jsonify({"success": False, "error": "Reset token is required."}), 400

    token_obj = PasswordResetToken.query.filter_by(token=token_str, used=False).first()
    if not token_obj:
        return jsonify({"success": False, "error": "Invalid or already-used reset link."}), 400

    if token_obj.is_expired(RESET_EXPIRY):
        return jsonify({"success": False,
                        "error": "This reset link has expired. Please request a new one."}), 400

    if len(new_pass) < 8:
        return jsonify({"success": False,
                        "error": "Password must be at least 8 characters.",
                        "field": "password"}), 422

    if new_pass != confirm:
        return jsonify({"success": False,
                        "error": "Passwords do not match.",
                        "field": "confirm_password"}), 422

    admin = Admin.query.get(token_obj.admin_id)
    admin.set_password(new_pass)
    token_obj.used = True
    db.session.commit()

    return jsonify({"success": True,
                    "data": {"message": "Password reset successfully. Please log in."}}), 200


# ── GET CURRENT SESSION INFO ──────────────────────────────────────────────────
@auth_bp.route("/me", methods=["GET"])
def me():
    if "admin_id" not in session:
        return jsonify({"success": False, "error": "Not logged in."}), 401
    return jsonify({
        "success": True,
        "data": {
            "id":        session["admin_id"],
            "email":     session["admin_email"],
            "full_name": session["admin_name"]
        }
    }), 200
