from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import date

class WorkExperience(db.Model):
    __tablename__ = 'work_experiences'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    
    company_name = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    current_work = db.Column(db.Boolean)
    description = db.Column(db.Text)

    # Relationships
    user = db.relationship("User", back_populates="work_experiences")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_name': self.company_name,
            'title': self.title,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'current_work': self.current_work,
            'description': self.description
        }
