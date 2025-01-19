from extensions import db
from models import BotMessage
from sqlalchemy import func

def get_messages_by_day():
    """Возвращает количество сообщений по дням."""
    result = db.session.query(
        func.date(BotMessage.timestamp).label('day'),
        func.count(BotMessage.id).label('message_count')
    ).group_by(func.date(BotMessage.timestamp)).all()
    return [{'day': str(row.day), 'message_count': row.message_count} for row in result]

def get_user_activity():
    """Возвращает количество сообщений по каждому юзеру."""
    result = db.session.query(
        BotMessage.username,
        func.count(BotMessage.id).label('message_count')
    ).group_by(BotMessage.username).all()
    return [{'username': row.username, 'message_count': row.message_count} for row in result]

def get_command_usage():
    """Возвращает количество использования каждой команды."""
    result = db.session.query(
        BotMessage.message_text,
        func.count(BotMessage.id).label('usage_count')
    ).filter(BotMessage.message_text.like('/%')).group_by(BotMessage.message_text).all()
    return [{'command': row.message_text, 'usage_count': row.usage_count} for row in result]
