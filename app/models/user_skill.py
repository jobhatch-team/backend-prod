from .db import db, environment, SCHEMA, add_prefix_for_prod

class UserSkill(db.Model):
    __tablename__ = 'user_skills'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('skills.id')), primary_key=True)

    proficiency_level = db.Column(db.String)
    years_of_experience = db.Column(db.Integer)

    user = db.relationship("User", back_populates="user_skills")
    skill = db.relationship("Skill", back_populates="user_skills")

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "proficiency_level": self.proficiency_level,
            "years_of_experience": self.years_of_experience
        }
