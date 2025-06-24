from .db import db, environment, SCHEMA, add_prefix_for_prod
from datetime import datetime
import sqlalchemy

class Profile(db.Model):
    __tablename__ = 'profiles'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), unique=True, nullable=False)

    location = db.Column(db.String)
    experience_years = db.Column(db.Integer)
    # preferred_roles = db.Column(db.ARRAY(db.String))
    # open_to_roles = db.Column(db.ARRAY(db.String))
    preferred_roles = db.Column(sqlalchemy.JSON, nullable=True)
    open_to_roles = db.Column(sqlalchemy.JSON, nullable=True)
    bio = db.Column(db.Text)

    github_url = db.Column(db.String)
    portfolio_url = db.Column(db.String)
    linkedin_url = db.Column(db.String)
    twitter_url = db.Column(db.String)

    achievements = db.Column(db.Text)
    pronouns = db.Column(db.String)
    gender = db.Column(db.String)
    ethnicity = db.Column(db.String)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    user = db.relationship("User", back_populates="profile")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'location': self.location,
            'experience_years': self.experience_years,
            'preferred_roles': self.preferred_roles,
            'open_to_roles': self.open_to_roles,
            'bio': self.bio,
            'github_url': self.github_url,
            'portfolio_url': self.portfolio_url,
            'linkedin_url': self.linkedin_url,
            'twitter_url': self.twitter_url,
            'achievements': self.achievements,
            'pronouns': self.pronouns,
            'gender': self.gender,
            'ethnicity': self.ethnicity,
            'created_at': self.created_at.isoformat()
        }
