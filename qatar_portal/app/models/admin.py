from app.extensions import db, bcrypt
from datetime import datetime, timezone


class Admin(db.Model):
    __tablename__ = "admins"

    id            = db.Column(db.Integer, primary_key=True)
    full_name     = db.Column(db.String(120), nullable=False)
    email         = db.Column(db.String(254), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    opportunities = db.relationship(
        "Opportunity",
        backref="owner",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )
    reset_tokens = db.relationship(
        "PasswordResetToken",
        backref="admin",
        lazy="dynamic",
        cascade="all, delete-orphan"
    )

    def set_password(self, raw_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(raw_password).decode("utf-8")

    def check_password(self, raw_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, raw_password)

    def to_dict(self) -> dict:
        return {
            "id":        self.id,
            "full_name": self.full_name,
            "email":     self.email
        }
