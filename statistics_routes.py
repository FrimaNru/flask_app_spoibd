from flask import Blueprint, jsonify
from messages_statistics import get_messages_by_day, get_user_activity, get_command_usage

statistics_bp = Blueprint('statistics', __name__)

@statistics_bp.route('/api/statistics', methods=['GET'])
def statistics():
    data = {
        'messages_by_day': get_messages_by_day(),
        'user_activity': get_user_activity(),
        'command_usage': get_command_usage()
    }
    return jsonify(data)
