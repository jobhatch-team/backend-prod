from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class Resume(db.Model):
    __tablename__ = 'resumes'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    file_url = db.Column(db.String(255), nullable=False)
    title = db.Column(db.String(255))
    extracted_text = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = db.relationship("User", back_populates="resumes")
    scores = db.relationship("ResumeScore", back_populates="resume", cascade="all, delete-orphan")
    job_matches = db.relationship("ResumeJobMatch", back_populates="resume", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "file_url": self.file_url,
            "title": self.title,
            "extracted_text": self.extracted_text,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
        }
