from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class PaymentRecord(db.Model):
    __tablename__ = 'payment_records'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    subscription_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('user_subscriptions.id')), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(10), server_default='USD')
    payment_method = db.Column(db.String(50))
    payment_date = db.Column(db.DateTime(timezone=True), server_default=func.now())
    status = db.Column(db.String(50), server_default='completed')
    transaction_id = db.Column(db.String(255))

    user = db.relationship("User", back_populates="payment_records")
    subscription = db.relationship("UserSubscription", back_populates="payments")

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'subscription_id': self.subscription_id,
            'amount': self.amount,
            'currency': self.currency,
            'payment_method': self.payment_method,
            'payment_date': self.payment_date,
            'status': self.status,
            'transaction_id': self.transaction_id,
        }
