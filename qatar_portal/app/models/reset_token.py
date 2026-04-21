from app.extensions import db
from datetime import datetime, timezone
import secrets


class PasswordResetToken(db.Model):
    __tablename__ = "password_reset_tokens"

    id         = db.Column(db.Integer, primary_key=True)
    admin_id   = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False)
    token      = db.Column(db.String(128), unique=True, nullable=False, index=True,
                           default=lambda: secrets.token_urlsafe(64))
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    used       = db.Column(db.Boolean, default=False)

    def is_expired(self, expiry_seconds: int) -> bool:
        created = self.created_at
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - created).total_seconds()
        return age > expiry_seconds
