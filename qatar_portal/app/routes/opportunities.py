from datetime import date
from flask import Blueprint, request, jsonify, session
from app.extensions import db
from app.models.opportunity import Opportunity
from app.utils.decorators import login_required

opps_bp = Blueprint("opportunities", __name__)

REQUIRED_FIELDS = [
    "name", "category", "duration", "start_date",
    "description", "skills_to_gain", "future_opportunities"
]


def _validate_opportunity(data: dict):
    for field in REQUIRED_FIELDS:
        val = data.get(field)
        if not val or (isinstance(val, str) and not val.strip()):
            label = field.replace("_", " ").title()
            return {"error": f"{label} is required.", "field": field}

    if data["category"] not in Opportunity.VALID_CATEGORIES:
        cats = ", ".join(sorted(Opportunity.VALID_CATEGORIES))
        return {"error": f"Category must be one of: {cats}", "field": "category"}

    try:
        date.fromisoformat(data["start_date"])
    except (ValueError, TypeError):
        return {"error": "Start Date must be a valid date (YYYY-MM-DD).", "field": "start_date"}

    max_app = data.get("max_applicants")
    if max_app not in (None, "", 0):
        try:
            val = int(max_app)
            if val < 1:
                raise ValueError
        except (TypeError, ValueError):
            return {"error": "Max Applicants must be a positive number.", "field": "max_applicants"}

    return None


# ── US-2.1  LIST ALL OPPORTUNITIES ───────────────────────────────────────────
@opps_bp.route("", methods=["GET"])
@login_required
def list_opportunities():
    admin_id = session["admin_id"]
    opps     = (Opportunity.query
                .filter_by(admin_id=admin_id)
                .order_by(Opportunity.created_at.desc())
                .all())
    return jsonify({"success": True, "data": [o.to_dict() for o in opps]}), 200


# ── US-2.2  CREATE OPPORTUNITY ────────────────────────────────────────────────
@opps_bp.route("", methods=["POST"])
@login_required
def create_opportunity():
    data = request.get_json(silent=True) or {}
    err  = _validate_opportunity(data)
    if err:
        return jsonify({"success": False, **err}), 422

    max_app = data.get("max_applicants")
    opp = Opportunity(
        admin_id             = session["admin_id"],
        name                 = data["name"].strip(),
        category             = data["category"],
        duration             = data["duration"].strip(),
        start_date           = date.fromisoformat(data["start_date"]),
        description          = data["description"].strip(),
        skills_to_gain       = data["skills_to_gain"].strip(),
        future_opportunities = data["future_opportunities"].strip(),
        max_applicants       = int(max_app) if max_app and str(max_app).strip() else None,
    )
    db.session.add(opp)
    db.session.commit()
    return jsonify({"success": True, "data": opp.to_dict()}), 201


# ── US-2.4  VIEW SINGLE OPPORTUNITY ──────────────────────────────────────────
@opps_bp.route("/<int:opp_id>", methods=["GET"])
@login_required
def get_opportunity(opp_id):
    opp = Opportunity.query.filter_by(id=opp_id, admin_id=session["admin_id"]).first()
    if not opp:
        return jsonify({"success": False, "error": "Opportunity not found."}), 404
    return jsonify({"success": True, "data": opp.to_dict()}), 200


# ── US-2.5  EDIT OPPORTUNITY ──────────────────────────────────────────────────
@opps_bp.route("/<int:opp_id>", methods=["PUT"])
@login_required
def edit_opportunity(opp_id):
    opp = Opportunity.query.filter_by(id=opp_id, admin_id=session["admin_id"]).first()
    if not opp:
        return jsonify({"success": False, "error": "Opportunity not found."}), 404

    data = request.get_json(silent=True) or {}
    err  = _validate_opportunity(data)
    if err:
        return jsonify({"success": False, **err}), 422

    max_app = data.get("max_applicants")
    opp.name                 = data["name"].strip()
    opp.category             = data["category"]
    opp.duration             = data["duration"].strip()
    opp.start_date           = date.fromisoformat(data["start_date"])
    opp.description          = data["description"].strip()
    opp.skills_to_gain       = data["skills_to_gain"].strip()
    opp.future_opportunities = data["future_opportunities"].strip()
    opp.max_applicants       = int(max_app) if max_app and str(max_app).strip() else None

    db.session.commit()
    return jsonify({"success": True, "data": opp.to_dict()}), 200


# ── US-2.6  DELETE OPPORTUNITY ────────────────────────────────────────────────
@opps_bp.route("/<int:opp_id>", methods=["DELETE"])
@login_required
def delete_opportunity(opp_id):
    opp = Opportunity.query.filter_by(id=opp_id, admin_id=session["admin_id"]).first()
    if not opp:
        return jsonify({"success": False, "error": "Opportunity not found."}), 404

    db.session.delete(opp)
    db.session.commit()
    return jsonify({"success": True, "data": {"deleted": True, "id": opp_id}}), 200
