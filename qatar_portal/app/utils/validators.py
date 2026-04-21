import re

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def validate_signup(data: dict):
    required = ["full_name", "email", "password", "confirm_password"]
    for field in required:
        if not str(data.get(field, "")).strip():
            label = field.replace("_", " ").title()
            return {"error": f"{label} is required.", "field": field}

    if not EMAIL_RE.match(data["email"]):
        return {"error": "Please enter a valid email address.", "field": "email"}

    if len(data["password"]) < 8:
        return {"error": "Password must be at least 8 characters.", "field": "password"}

    if data["password"] != data["confirm_password"]:
        return {"error": "Passwords do not match.", "field": "confirm_password"}

    return None


def validate_login(data: dict):
    if not str(data.get("email", "")).strip():
        return {"error": "Email is required.", "field": "email"}
    if not str(data.get("password", "")).strip():
        return {"error": "Password is required.", "field": "password"}
    return None
