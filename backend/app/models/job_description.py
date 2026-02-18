from datetime import UTC, datetime

from app.extensions import db


class JobDescription(db.Model):
    __tablename__ = "job_descriptions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(120), nullable=True)
    level = db.Column(db.String(120), nullable=True)
    location = db.Column(db.String(120), nullable=True)
    text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(UTC), nullable=False
    )
    applications = db.relationship(
        "Application", back_populates="job_description", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "department": self.department,
            "level": self.level,
            "location": self.location,
            "text": self.text,
            "created_at": self.created_at.isoformat(),
        }
