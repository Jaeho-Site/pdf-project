# -*- coding: utf-8 -*-
"""
인증 미들웨어 - 세션 또는 헤더 기반 인증
"""
from flask import session, request, jsonify
from functools import wraps

def check_auth():
    """인증 확인 - 세션 또는 헤더"""
    # 1. 세션 확인
    if 'user_id' in session:
        return True
    
    # 2. 헤더 확인
    user_id = request.headers.get('X-User-ID')
    user_role = request.headers.get('X-User-Role')
    user_email = request.headers.get('X-User-Email')
    
    if user_id and user_role and user_email:
        # 헤더 정보를 세션에 저장
        session['user_id'] = user_id
        session['role'] = user_role
        session['email'] = user_email
        return True
    
    return False

def require_auth(f):
    """인증 필요 데코레이터 - 세션 또는 헤더 확인"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not check_auth():
            return jsonify({
                'success': False,
                'message': '로그인이 필요합니다.'
            }), 401
        return f(*args, **kwargs)
    
    return decorated_function

def get_current_user():
    """현재 사용자 정보 가져오기"""
    return {
        'user_id': session.get('user_id'),
        'role': session.get('role'),
        'email': session.get('email')
    }

