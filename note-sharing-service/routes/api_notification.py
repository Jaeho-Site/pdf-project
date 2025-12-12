# -*- coding: utf-8 -*-
"""
API 알림 라우트 (JSON 응답)
"""
from flask import Blueprint, jsonify, session, request
from services.database_service import DatabaseService
from utils.auth_middleware import check_auth

api_notification_bp = Blueprint('api_notification', __name__)
db = DatabaseService()

@api_notification_bp.route('', methods=['GET', 'OPTIONS'])
def get_notifications():
    """알림 목록 조회"""
    auth_result = check_auth()
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    notifications = db.get_notifications_by_user(user_id)
    
    return jsonify({
        'success': True,
        'notifications': notifications
    }), 200

@api_notification_bp.route('/<notification_id>/read', methods=['POST', 'OPTIONS'])
def mark_as_read(notification_id):
    """알림 읽음 처리"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth()
    if auth_result:
        return auth_result
    
    db.mark_notification_as_read(notification_id)
    
    return jsonify({
        'success': True,
        'message': '읽음 처리되었습니다.'
    }), 200

@api_notification_bp.route('/unread-count', methods=['GET', 'OPTIONS'])
def get_unread_count():
    """읽지 않은 알림 개수"""
    auth_result = check_auth()
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    count = db.get_unread_notification_count(user_id)
    
    return jsonify({
        'success': True,
        'count': count
    }), 200

