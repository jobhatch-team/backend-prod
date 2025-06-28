from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class Message(db.Model):
    __tablename__ = 'messages'

    if environment == "production":
        __table_args__ = {'schema': SCHEMA}

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('conversations.id')), nullable=False)
    sender_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    message_body = db.Column(db.Text, nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    read_at = db.Column(db.DateTime(timezone=True), nullable=True)
    is_recalled = db.Column(db.Boolean, nullable=False, server_default='0')
    edited_at = db.Column(db.DateTime(timezone=True), nullable=True)

    conversation = db.relationship("Conversation", back_populates="messages")
    sender = db.relationship("User", back_populates="messages_sent", foreign_keys=[sender_id])

    def to_dict(self):
        return {
            'id': self.id,
            'conversation_id': self.conversation_id,
            'sender_id': self.sender_id,
            'message_body': self.message_body if not self.is_recalled else "This message has been recalled",
            'sent_at': self.sent_at,
            'read_at': self.read_at,
            'is_recalled': self.is_recalled,
            'edited_at': self.edited_at
        }
