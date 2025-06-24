from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class ResumeScore(db.Model):
    __tablename__ = 'resume_scores'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    resume_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('resumes.id')), nullable=False)
    ai_model = db.Column(db.String(100))
    score_overall = db.Column(db.Float)
    score_format = db.Column(db.Float)
    score_skills = db.Column(db.Float)
    score_experience = db.Column(db.Float)
    strengths = db.Column(db.Text)
    weaknesses = db.Column(db.Text)
    suggestions = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    resume = db.relationship("Resume", back_populates="scores")

    def to_dict(self):
        return {
            "id": self.id,
            "resume_id": self.resume_id,
            "ai_model": self.ai_model,
            "score_overall": self.score_overall,
            "score_format": self.score_format,
            "score_skills": self.score_skills,
            "score_experience": self.score_experience,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "suggestions": self.suggestions,
            "evaluated_at": self.evaluated_at.isoformat() if self.evaluated_at else None,
        }
