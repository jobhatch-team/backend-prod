from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class ResumeJobMatch(db.Model):
    __tablename__ = 'resume_job_matches'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('resumes.id')), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('jobs.id')), nullable=False)
    match_score = db.Column(db.Float)
    match_summary = db.Column(db.Text)
    matched_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = db.relationship("Resume", back_populates="job_matches")
    job = db.relationship("Job", back_populates="resume_matches")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "job_id": self.job_id,
            "match_score": self.match_score,
            "match_summary": self.match_summary,
            "matched_at": self.matched_at.isoformat() if self.matched_at else None,
        }

