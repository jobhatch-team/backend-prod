from .db import db, environment, SCHEMA, add_prefix_for_prod

class Skill(db.Model):
    __tablename__ = 'skills'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)

    user_skills = db.relationship("UserSkill", back_populates="skill", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name
        }
