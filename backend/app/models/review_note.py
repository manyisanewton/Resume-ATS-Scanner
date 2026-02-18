from datetime import UTC, datetime

from app.extensions import db


class ReviewNote(db.Model):
    __tablename__ = "review_notes"

    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(
        db.Integer, db.ForeignKey("applications.id"), nullable=False
    )
    author_name = db.Column(db.String(120), nullable=False)
    note_text = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    application = db.relationship("Application", back_populates="notes")

    def to_dict(self):
        return {
            "id": self.id,
            "application_id": self.application_id,
            "author_name": self.author_name,
            "note_text": self.note_text,
            "created_at": self.created_at.isoformat(),
        }
