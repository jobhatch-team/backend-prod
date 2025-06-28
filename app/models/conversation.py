from .db import db, environment, SCHEMA, add_prefix_for_prod
from sqlalchemy.sql import func

class Conversation(db.Model):
    __tablename__ = 'conversations'

    if environment == "production":
        __table_args__ = (
            db.UniqueConstraint('user_1_id', 'user_2_id', name='unique_conversation_between_users'),
            {'schema': SCHEMA}
        )

    id = db.Column(db.Integer, primary_key=True)
    user_1_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    user_2_id = db.Column(db.Integer, db.ForeignKey(add_prefix_for_prod('users.id')), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), server_default=func.now())
    deleted_by_user_1 = db.Column(db.Boolean, nullable=False, server_default='0')
    deleted_by_user_2 = db.Column(db.Boolean, nullable=False, server_default='0')


    user_1 = db.relationship("User", back_populates="conversations_1", foreign_keys=[user_1_id])
    user_2 = db.relationship("User", back_populates="conversations_2", foreign_keys=[user_2_id])
    messages = db.relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    @classmethod
    def get_or_create(cls, user_a_id, user_b_id):
        user_1_id, user_2_id = sorted([user_a_id, user_b_id])
        
        conversation = cls.query.filter_by(user_1_id=user_1_id, user_2_id=user_2_id).first()
        if conversation:
            return conversation
        
        conversation = cls(user_1_id=user_1_id, user_2_id=user_2_id)
        db.session.add(conversation)
        db.session.commit()
        return conversation

    def to_dict(self, current_user_id=None):
        if current_user_id:
            if (current_user_id == self.user_1_id and self.deleted_by_user_1) or \
               (current_user_id == self.user_2_id and self.deleted_by_user_2):
                return None
        return {
            'id': self.id,
            'user_1_id': self.user_1_id,
            'user_2_id': self.user_2_id,
            'created_at': self.created_at,
            'deleted_by_user_1': self.deleted_by_user_1,
            'deleted_by_user_2': self.deleted_by_user_2,
        }

