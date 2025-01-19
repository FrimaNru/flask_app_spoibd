import uuid
from extensions import db

class Fact(db.Model):
    __tablename__ = 'facts'
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))  # Генерация UUID
    text = db.Column(db.String(50), nullable=False)

class BotMessage(db.Model):
    __tablename__ = 'bot_messages'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.BigInteger, nullable=False)
    username = db.Column(db.String(50), nullable=True)
    chat_id = db.Column(db.BigInteger, nullable=False)
    message_text = db.Column(db.Text, nullable=False)
    message_type = db.Column(db.String(20), default='text')
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Admin(db.Model):
    __tablename__ = 'admins'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False)
