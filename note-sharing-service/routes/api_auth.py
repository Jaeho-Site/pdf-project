# -*- coding: utf-8 -*-
"""
API 인증 라우트 (JSON 응답)
"""
from flask import Blueprint, request, jsonify, session
from services.database_service import DatabaseService

api_auth_bp = Blueprint('api_auth', __name__)
db = DatabaseService()

@api_auth_bp.route('/signup', methods=['POST'])
def signup():
    """API 회원가입 (JSON)"""
    data = request.get_json()
    
    # 필수 필드 검증
    required_fields = ['email', 'password', 'name', 'role']
    for field in required_fields:
        if not data.get(field):
            return jsonify({
                'success': False,
                'message': f'{field}은(는) 필수 항목입니다.'
            }), 400
    
    # 이메일 형식 검증
    email = data.get('email')
    if '@' not in email:
        return jsonify({
            'success': False,
            'message': '올바른 이메일 형식이 아닙니다.'
        }), 400
    
    # 역할 검증
    role = data.get('role')
    if role not in ['student', 'professor']:
        return jsonify({
            'success': False,
            'message': '역할은 student 또는 professor만 가능합니다.'
        }), 400
    
    try:
        user_data = {
            'email': email,
            'password': data.get('password'),
            'name': data.get('name'),
            'role': role
        }
        
        user_id = db.create_user(user_data)
        
        print("=" * 70)
        print(f"[SIGNUP] 회원가입 성공!")
        print(f"  - 이메일: {email}")
        print(f"  - 사용자: {data.get('name')} ({role})")
        print(f"  - User ID: {user_id}")
        print("=" * 70)
        
        return jsonify({
            'success': True,
            'message': '회원가입이 완료되었습니다. 로그인해주세요.',
            'user_id': user_id
        }), 201
        
    except ValueError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        }), 400
    except Exception as e:
        print(f"[ERROR] 회원가입 실패: {e}")
        return jsonify({
            'success': False,
            'message': '회원가입 중 오류가 발생했습니다.'
        }), 500

@api_auth_bp.route('/login', methods=['POST'])
def login():
    """API 로그인 (JSON)"""
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    
    user = db.authenticate_user(email, password)
    
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
    
    user = db.get_user_by_id(session['user_id'])
    
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

@api_auth_bp.route('/init-demo-users', methods=['POST'])
def init_demo_users():
    """데모 사용자 생성 - 초기 설정용"""
    try:
        # 교수가 있는지 확인
        professor = db.get_user_by_email('kim.prof@university.ac.kr')
        if professor:
            existing_users = db.get_all_users()
            return jsonify({
                'success': True,
                'message': f'이미 {len(existing_users)}명의 사용자가 존재합니다. (교수 포함)',
                'user_count': len(existing_users)
            }), 200
        
        # 테스트 사용자 생성
        test_users = [
            # 교수
            {
                'email': 'kim.prof@university.ac.kr',
                'password': 'prof1234',
                'name': '김교수',
                'role': 'professor'
            },
            {
                'email': 'lee.prof@university.ac.kr',
                'password': 'prof5678',
                'name': '이교수',
                'role': 'professor'
            },
            # 학생
            {
                'email': 'hong@student.ac.kr',
                'password': 'student1',
                'name': '홍길동',
                'role': 'student'
            },
            {
                'email': 'kim@student.ac.kr',
                'password': 'student2',
                'name': '김철수',
                'role': 'student'
            },
            {
                'email': 'lee@student.ac.kr',
                'password': 'student3',
                'name': '이영희',
                'role': 'student'
            }
        ]
        
        created_users = []
        for user_data in test_users:
            try:
                user_id = db.create_user(user_data)
                created_users.append({
                    'user_id': user_id,
                    'email': user_data['email'],
                    'name': user_data['name'],
                    'role': user_data['role']
                })
            except ValueError as e:
                # 이미 존재하는 경우 무시
                pass
        
        return jsonify({
            'success': True,
            'message': f'{len(created_users)}명의 테스트 사용자가 생성되었습니다.',
            'users': created_users
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'사용자 생성 실패: {str(e)}'
        }), 500
