from datetime import UTC, datetime

from app.extensions import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(200), nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    resume_filename = db.Column(db.String(255), nullable=False)
    resume_path = db.Column(db.String(500), nullable=False)
    extracted_text = db.Column(db.Text, nullable=True)
    profile_json = db.Column(db.JSON, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    applications = db.relationship(
        "Application", back_populates="candidate", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "phone": self.phone,
            "resume_filename": self.resume_filename,
            "resume_path": self.resume_path,
            "extracted_text": self.extracted_text,
            "profile_json": self.profile_json,
            "created_at": self.created_at.isoformat(),
        }
