from .db import db, environment, SCHEMA
from sqlalchemy.sql import func

class Job(db.Model):
    __tablename__ = 'jobs'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    work_experience = db.Column(db.Integer)
    skills = db.Column(db.String(255))
    location = db.Column(db.String(255))
    accept_relocate = db.Column(db.Boolean)
    offer_relocate_assistance = db.Column(db.Boolean)
    offer_visa_sponsorship = db.Column(db.Boolean)
    is_remote = db.Column(db.Boolean, default=False)
    currency = db.Column(db.String(10))
    salary_min = db.Column(db.Integer)
    salary_max = db.Column(db.Integer)
    equity_min = db.Column(db.Float)
    equity_max = db.Column(db.Float)
    job_type = db.Column(db.String(50))
    company_id = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.companies.id" if environment == "production" else "companies.id"))
    posted_by = db.Column(db.Integer, db.ForeignKey(f"{SCHEMA}.users.id" if environment == "production" else "users.id"))
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    status = db.Column(db.String(50), default='open')

    # Relationships
    company = db.relationship("Company", back_populates="jobs")
    poster = db.relationship("User", back_populates="jobs_posted")

    applications = db.relationship("Application", back_populates="job", cascade="all, delete-orphan")
    resume_matches = db.relationship("ResumeJobMatch", back_populates="job", cascade="all, delete-orphan")


    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "work_experience": self.work_experience,
            "skills": self.skills,
            "location": self.location,
            "accept_relocate": self.accept_relocate,
            "offer_relocate_assistance": self.offer_relocate_assistance,
            "offer_visa_sponsorship": self.offer_visa_sponsorship,
            "is_remote": self.is_remote,
            "currency": self.currency,
            "salary_min": self.salary_min,
            "salary_max": self.salary_max,
            "equity_min": self.equity_min,
            "equity_max": self.equity_max,
            "job_type": self.job_type,
            "company_id": self.company_id,
            "posted_by": self.posted_by,
            "created_at": self.created_at,
            "status": self.status,
        }
