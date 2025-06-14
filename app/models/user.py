from .db import db, environment, SCHEMA, add_prefix_for_prod
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from sqlalchemy.sql import func


class User(db.Model, UserMixin):
    __tablename__ = 'users'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), nullable=False, unique=True)
    email = db.Column(db.String(255), nullable=False, unique=True)
    hashed_password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(50))  # e.g. job_seeker, recruiter, founder
    avatar_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    profile = db.relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    work_experiences = db.relationship("WorkExperience", back_populates="user", cascade="all, delete-orphan")
    education_experiences = db.relationship("EducationExperience", back_populates="user", cascade="all, delete-orphan")
    applications = db.relationship("Application", back_populates="user", cascade="all, delete-orphan")
    user_preference = db.relationship("UserPreference", back_populates="user", uselist=False, cascade="all, delete-orphan")
    messages_sent = db.relationship("Message", back_populates="sender", foreign_keys="[Message.sender_id]")
    conversations_1 = db.relationship("Conversation", back_populates="user_1", foreign_keys="[Conversation.user_1_id]")
    conversations_2 = db.relationship("Conversation", back_populates="user_2", foreign_keys="[Conversation.user_2_id]")

    jobs_posted = db.relationship("Job", back_populates="poster", cascade="all, delete-orphan")
    user_skills = db.relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def password(self):
        return self.hashed_password

    @password.setter
    def password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'avatar_url': self.avatar_url,
            'created_at': self.created_at
        }
