from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import date

class EducationExperience(db.Model):
    __tablename__ = 'education_experiences'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)

    school_name = db.Column(db.String, nullable=False)
    graduation = db.Column(db.Boolean)
    degree = db.Column(db.String)
    major = db.Column(db.String)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    gpa = db.Column(db.String)

    # Relationships
    user = db.relationship("User", back_populates="education_experiences")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'school_name': self.school_name,
            'graduation': self.graduation,
            'degree': self.degree,
            'major': self.major,
            'start_date': self.start_date.isoformat() if self.start_date else None,
            'end_date': self.end_date.isoformat() if self.end_date else None,
            'gpa': self.gpa
        }
