from .db import db, environment, SCHEMA
from sqlalchemy.sql import func

class Company(db.Model):
    __tablename__ = 'companies'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    website = db.Column(db.String(255))
    logo_url = db.Column(db.String(255))
    description = db.Column(db.Text)
    location = db.Column(db.String(255))
    funding_stage = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    jobs = db.relationship("Job", back_populates="company", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "website": self.website,
            "logo_url": self.logo_url,
            "description": self.description,
            "location": self.location,
            "funding_stage": self.funding_stage,
            "created_at": self.created_at
        }
