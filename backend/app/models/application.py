from datetime import UTC, datetime

from app.extensions import db


class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey("candidates.id"), nullable=False)
    jd_id = db.Column(db.Integer, db.ForeignKey("job_descriptions.id"), nullable=False)
    total_score = db.Column(db.Float, nullable=True)
    status = db.Column(db.String(50), default="new", nullable=False)
    score_breakdown_json = db.Column(db.JSON, nullable=True)
    reviewed_by = db.Column(db.String(120), nullable=True)
    reviewed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(UTC), nullable=False
    )

    candidate = db.relationship("Candidate", back_populates="applications")
    job_description = db.relationship("JobDescription", back_populates="applications")
    notes = db.relationship(
        "ReviewNote", back_populates="application", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "candidate_id": self.candidate_id,
            "jd_id": self.jd_id,
            "total_score": self.total_score,
            "status": self.status,
            "score_breakdown_json": self.score_breakdown_json,
            "reviewed_by": self.reviewed_by,
            "reviewed_at": self.reviewed_at.isoformat() if self.reviewed_at else None,
            "created_at": self.created_at.isoformat(),
        }
