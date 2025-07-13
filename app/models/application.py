from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class Application(db.Model):
    __tablename__ = 'applications'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('jobs.id')), nullable=False)
    cover_letter = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    applied_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    user = db.relationship("User", back_populates="applications")
    job = db.relationship("Job", back_populates="applications")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'job_id': self.job_id,
            'cover_letter': self.cover_letter,
            'status': self.status,
            'applied_at': self.applied_at
        }
