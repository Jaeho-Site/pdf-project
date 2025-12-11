# -*- coding: utf-8 -*-
"""
API 알림 라우트 (JSON 응답)
"""
from flask import Blueprint, jsonify, session
from services.database_service import DatabaseService

api_notification_bp = Blueprint('api_notification', __name__)
db = DatabaseService()

def require_login():
    """로그인 확인"""
    if 'user_id' not in session:
        return False
    return True

@api_notification_bp.route('', methods=['GET'])
def get_notifications():
    """알림 목록 조회"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    notifications = db.get_notifications_by_user(user_id)
    
    return jsonify({
        'success': True,
        'notifications': notifications
    }), 200

@api_notification_bp.route('/<notification_id>/read', methods=['POST'])
def mark_as_read(notification_id):
    """알림 읽음 처리"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    db.mark_notification_as_read(notification_id)
    
    return jsonify({
        'success': True,
        'message': '읽음 처리되었습니다.'
    }), 200

@api_notification_bp.route('/unread-count', methods=['GET'])
def get_unread_count():
    """읽지 않은 알림 개수"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    count = db.get_unread_notification_count(user_id)
    
    return jsonify({
        'success': True,
        'count': count
    }), 200

