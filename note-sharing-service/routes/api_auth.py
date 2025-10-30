# -*- coding: utf-8 -*-
"""
API 인증 라우트 (JSON 응답)
"""
from flask import Blueprint, request, jsonify, session
from services.data_service import DataService

api_auth_bp = Blueprint('api_auth', __name__)
data_service = DataService()

@api_auth_bp.route('/login', methods=['POST'])
def login():
    """API 로그인 (JSON)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = data_service.authenticate_user(email, password)
    
    if user:
        # 세션 설정
        session['user_id'] = user['user_id']
        session['name'] = user['name']
        session['role'] = user['role']
        session['email'] = user['email']
        
        print("=" * 70)
        print(f"[LOGIN] 로그인 성공!")
        print(f"  - 이메일: {email}")
        print(f"  - 사용자: {user['name']} ({user['role']})")
        print(f"  - User ID: {user['user_id']}")
        print(f"  - Session ID: {session.get('_id', 'N/A')}")
        print(f"  - 세션 저장: user_id={session['user_id']}, role={session['role']}")
        print("=" * 70)
        
        # 비밀번호 제외하고 반환
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'message': f'{user["name"]}님 환영합니다!',
            'user': user_data
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '이메일 또는 비밀번호가 올바르지 않습니다.'
        }), 401

@api_auth_bp.route('/logout', methods=['POST'])
def logout():
    """API 로그아웃"""
    session.clear()
    return jsonify({
        'success': True,
        'message': '로그아웃되었습니다.'
    }), 200

@api_auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """현재 로그인한 사용자 정보"""
    if 'user_id' not in session:
        return jsonify({
            'success': False,
            'message': '로그인이 필요합니다.'
        }), 401
    
    user = data_service.get_user_by_id(session['user_id'])
    
    if user:
        user_data = {k: v for k, v in user.items() if k != 'password'}
        return jsonify({
            'success': True,
            'user': user_data
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '사용자를 찾을 수 없습니다.'
        }), 404

