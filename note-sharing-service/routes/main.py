# -*- coding: utf-8 -*-
"""
메인 페이지 라우트
"""
from flask import Blueprint, render_template, session
from services.data_service import DataService
from utils.helpers import login_required

main_bp = Blueprint('main', __name__)
data_service = DataService()

@main_bp.route('/')
def index():
    """메인 페이지 (로그인 전/후 구분)"""
    if 'user_id' not in session:
        # 로그인 전: 로그인 페이지로 리다이렉트
        from flask import redirect, url_for
        return redirect(url_for('auth.login'))
    
    user_id = session['user_id']
    role = session['role']
    
    # 로그인 후: 강의 목록 표시
    if role == 'professor':
        courses = data_service.get_courses_by_professor(user_id)
    else:
        courses = data_service.get_courses_by_student(user_id)
    
    # 알림 개수
    unread_count = data_service.get_unread_notification_count(user_id)
    
    return render_template('main.html', 
                         courses=courses,
                         unread_count=unread_count)

@main_bp.route('/notifications')
@login_required
def notifications():
    """알림 목록"""
    user_id = session['user_id']
    notifications = data_service.get_notifications_by_user(user_id)
    
    return render_template('notifications.html', notifications=notifications)

@main_bp.route('/notifications/<notification_id>/read', methods=['POST'])
@login_required
def mark_notification_read(notification_id):
    """알림 읽음 처리"""
    data_service.mark_notification_as_read(notification_id)
    
    from flask import redirect, url_for
    return redirect(url_for('main.notifications'))

