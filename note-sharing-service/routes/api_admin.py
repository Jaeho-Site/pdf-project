# -*- coding: utf-8 -*-
"""
관리자 API - 데이터 관리용
"""
from flask import Blueprint, request, jsonify
from services.database_service import DatabaseService

api_admin_bp = Blueprint('api_admin', __name__)
db = DatabaseService()

@api_admin_bp.route('/users', methods=['GET'])
def get_all_users():
    """모든 사용자 조회"""
    users = db.get_all_users()
    # 비밀번호 제외
    safe_users = [{k: v for k, v in u.items() if k != 'password'} for u in users]
    return jsonify({
        'success': True,
        'count': len(safe_users),
        'users': safe_users
    }), 200

@api_admin_bp.route('/courses', methods=['GET'])
def get_all_courses():
    """모든 강의 조회"""
    courses = db.get_all_courses()
    return jsonify({
        'success': True,
        'count': len(courses),
        'courses': courses
    }), 200

@api_admin_bp.route('/seed-users', methods=['POST'])
def seed_users():
    """사용자 대량 생성"""
    data = request.get_json()
    users = data.get('users', [])
    
    created = []
    errors = []
    
    for user_data in users:
        try:
            user_id = db.create_user(user_data)
            created.append({'user_id': user_id, 'email': user_data['email']})
        except ValueError as e:
            errors.append({'email': user_data.get('email'), 'error': str(e)})
    
    return jsonify({
        'success': True,
        'created': len(created),
        'errors': len(errors),
        'users': created,
        'error_details': errors
    }), 201

@api_admin_bp.route('/seed-courses', methods=['POST'])
def seed_courses():
    """강의 대량 생성"""
    data = request.get_json()
    courses = data.get('courses', [])
    
    created = []
    errors = []
    
    for course_data in courses:
        try:
            # 교수 확인
            professor = db.get_user_by_email(course_data.get('professor_email'))
            if not professor:
                errors.append({'course': course_data.get('course_name'), 'error': '교수를 찾을 수 없음'})
                continue
            
            # 강의 생성
            course = {
                'course_name': course_data['course_name'],
                'professor_id': professor['user_id'],
                'professor_name': professor['name'],
                'enrolled_students': []
            }
            
            course_id = db.add_course(course)
            
            # 주차별 마감일 설정 (옵션)
            if 'deadline' in course_data and 'weeks' in course_data:
                for week in range(1, course_data['weeks'] + 1):
                    db.set_week_deadline(course_id, week, course_data['deadline'])
            
            # 초대 코드 생성 (옵션)
            invitation_code = None
            if course_data.get('create_invitation', False):
                invitation_code = db.create_invitation(
                    course_id=course_id,
                    created_by=professor['user_id'],
                    expires_at=None,
                    max_uses=-1
                )
            
            created.append({
                'course_id': course_id,
                'course_name': course_data['course_name'],
                'invitation_code': invitation_code
            })
            
        except Exception as e:
            errors.append({'course': course_data.get('course_name'), 'error': str(e)})
    
    return jsonify({
        'success': True,
        'created': len(created),
        'errors': len(errors),
        'courses': created,
        'error_details': errors
    }), 201

@api_admin_bp.route('/reset-db', methods=['POST'])
def reset_db():
    """DB 초기화 (위험!)"""
    # 보안을 위해 특정 키 필요
    data = request.get_json() or {}
    secret = data.get('secret')
    
    if secret != 'RESET_DB_2024':
        return jsonify({'success': False, 'message': '권한이 없습니다.'}), 403
    
    import os
    from config import Config
    
    # 플래그 파일 삭제
    flag_file = os.path.join(Config.DATA_DIR, '.initialized')
    if os.path.exists(flag_file):
        os.remove(flag_file)
    
    # DB 파일 삭제
    db_file = os.path.join(Config.DATA_DIR, 'database.db')
    if os.path.exists(db_file):
        os.remove(db_file)
    
    return jsonify({
        'success': True,
        'message': 'DB가 초기화되었습니다. 서버를 재시작하세요.'
    }), 200

