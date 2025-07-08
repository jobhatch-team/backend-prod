from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    tagline = db.Column(db.String(255))
    description = db.Column(db.Text)
    price = db.Column(db.Float, nullable=False)
    billing_cycle = db.Column(db.String(50), nullable=False)  # e.g., monthly, yearly
    for_role = db.Column(db.String(50))  # e.g., job_seeker, recruiter
    feature_flags = db.Column(db.Text)  # optional: JSON string
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())

    # Relationships
    subscriptions = db.relationship("UserSubscription", back_populates="plan", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "tagline": self.tagline,
            "description": self.description,
            "price": self.price,
            "billing_cycle": self.billing_cycle,
            "for_role": self.for_role,
            "feature_flags": self.feature_flags,
            "created_at": self.created_at,
        }
