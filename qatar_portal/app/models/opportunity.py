from app.extensions import db
from datetime import datetime, timezone


class Opportunity(db.Model):
    __tablename__ = "opportunities"

    id                   = db.Column(db.Integer, primary_key=True)
    admin_id             = db.Column(db.Integer, db.ForeignKey("admins.id"), nullable=False, index=True)
    name                 = db.Column(db.String(200), nullable=False)
    category             = db.Column(db.String(50), nullable=False)
    duration             = db.Column(db.String(100), nullable=False)
    start_date           = db.Column(db.Date, nullable=False)
    description          = db.Column(db.Text, nullable=False)
    skills_to_gain       = db.Column(db.Text, nullable=False)
    future_opportunities = db.Column(db.Text, nullable=False)
    max_applicants       = db.Column(db.Integer, nullable=True)
    created_at           = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at           = db.Column(db.DateTime,
                                     default=lambda: datetime.now(timezone.utc),
                                     onupdate=lambda: datetime.now(timezone.utc))

    VALID_CATEGORIES = {"Technology", "Business", "Design", "Marketing", "Data Science", "Other"}

    def to_dict(self) -> dict:
        return {
            "id":                   self.id,
            "name":                 self.name,
            "category":             self.category,
            "duration":             self.duration,
            "start_date":           self.start_date.isoformat(),
            "description":          self.description,
            "skills_to_gain":       self.skills_to_gain,
            "future_opportunities": self.future_opportunities,
            "max_applicants":       self.max_applicants,
            "created_at":           self.created_at.isoformat(),
        }
