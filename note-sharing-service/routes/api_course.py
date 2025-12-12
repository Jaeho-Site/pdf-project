# -*- coding: utf-8 -*-
"""
API 강의 라우트 (JSON 응답) - SQLite + GCS 버전
"""
from flask import Blueprint, request, jsonify, session
from services.database_service import DatabaseService
from utils.auth_middleware import check_auth

api_course_bp = Blueprint('api_course', __name__)
db = DatabaseService()

@api_course_bp.route('', methods=['GET'])
def get_courses():
    """강의 목록 조회"""
    auth_result = check_auth()
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    role = request.headers.get('X-User-Role')
    
    if role == 'professor':
        courses = db.get_courses_by_professor(user_id)
    else:
        courses = db.get_courses_by_student(user_id)
    
    return jsonify({
        'success': True,
        'courses': courses
    }), 200

@api_course_bp.route('/<course_id>', methods=['GET'])
def get_course_detail(course_id):
    """강의 상세 조회"""
    auth_result = check_auth()
    if auth_result:
        return auth_result
    
    course = db.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    # 주차별 자료 통계
    weeks_data = []
    for week in range(1, 17):
        materials = db.get_materials_by_course_week(course_id, week)
        professor_materials = [m for m in materials if m['type'] == 'professor']
        student_materials = [m for m in materials if m['type'] == 'student']
        
        weeks_data.append({
            'week': week,
            'professor_count': len(professor_materials),
            'student_count': len(student_materials),
            'total_downloads': sum(m['download_count'] for m in materials),
            'total_views': sum(m['view_count'] for m in materials)
        })
    
    return jsonify({
        'success': True,
        'course': course,
        'weeks_data': weeks_data
    }), 200

@api_course_bp.route('/<course_id>/week/<int:week>', methods=['GET'])
def get_week_materials(course_id, week):
    """주차별 자료 조회"""
    try:
        auth_result = check_auth()
        if auth_result:
            return auth_result
        
        course = db.get_course_by_id(course_id)
        
        if not course:
            return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
        
        # 학생인 경우 마감일 체크 (열람 가능 여부)
        role = request.headers.get('X-User-Role')
        can_view = True
        if role == 'student':
            can_view = db.can_view_materials(course_id, week)
        
        materials = db.get_materials_by_course_week(course_id, week)
        
        professor_materials = [m for m in materials if m['type'] == 'professor']
        student_materials = [m for m in materials if m['type'] == 'student']
        
        # 학생 자료는 마감일이 지나지 않았으면 숨김 (본인 자료는 항상 표시)
        if role == 'student' and not can_view:
            user_id = session.get('user_id')
            student_materials = [m for m in student_materials if m.get('uploader_id') == user_id]
        
        # 정렬
        sort_by = request.args.get('sort', 'latest')
        if sort_by == 'name':
            student_materials.sort(key=lambda x: x.get('uploader_name', ''))
        elif sort_by == 'popular':
            student_materials.sort(key=lambda x: x.get('view_count', 0), reverse=True)
        elif sort_by == 'downloads':
            student_materials.sort(key=lambda x: x.get('download_count', 0), reverse=True)
        elif sort_by == 'score':
            student_materials.sort(key=lambda x: (
                x.get('evaluation_score') is None,
                -(x.get('evaluation_score') or 0)
            ))
        else:
            student_materials.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        
        # 마감일 정보
        deadline = db.get_week_deadline(course_id, week)
        weeks_config = course.get('weeks', {})
        week_str = str(week)
        evaluation_status = weeks_config.get(week_str, {}).get('evaluation_status', 'pending') if week_str in weeks_config else 'pending'
        
        # 업로드 가능 여부
        can_upload = True if role == 'professor' else db.is_upload_period_open(course_id, week)
        
        return jsonify({
            'success': True,
            'course': course,
            'professor_materials': professor_materials,
            'student_materials': student_materials,
            'upload_deadline': deadline,
            'can_upload': can_upload,
            'can_view': can_view if role == 'student' else True,
            'evaluation_status': evaluation_status
        }), 200
    except Exception as e:
        print(f"[ERROR] get_week_materials: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'자료 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

@api_course_bp.route('/create', methods=['POST', 'OPTIONS'])
def create_course():
    """강의 생성 (교수만)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth(required_role='professor')
    if auth_result:
        return auth_result
    
    data = request.get_json()
    professor_id = request.headers.get('X-User-ID')
    professor = db.get_user_by_id(professor_id)
    
    course = {
        'course_name': data.get('course_name'),
        'professor_id': professor_id,
        'professor_name': professor['name'],
        'enrolled_students': []
    }
    
    course_id = db.add_course(course)
    
    return jsonify({
        'success': True,
        'message': f'강의 "{course["course_name"]}"이(가) 생성되었습니다.',
        'course_id': course_id
    }), 201

@api_course_bp.route('/init-demo-course', methods=['POST', 'OPTIONS'])
def init_demo_course():
    """데모 강의 생성 (심화프로젝트랩) - 관리자용"""
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        # 이미 존재하는지 확인
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT course_id FROM courses WHERE course_name = '심화프로젝트랩'")
            existing = cursor.fetchone()
            
            if existing:
                # 기존 강의의 초대 코드 반환
                invitations = db.get_invitations_by_course(existing['course_id'])
                if invitations:
                    return jsonify({
                        'success': True,
                        'message': '이미 존재하는 강의입니다.',
                        'course_id': existing['course_id'],
                        'invitation_code': invitations[0]['invitation_code']
                    }), 200
        
        # 김교수 계정 확인
        professor = db.get_user_by_email('kim.prof@university.ac.kr')
        if not professor:
            return jsonify({'success': False, 'message': '교수 계정을 찾을 수 없습니다.'}), 404
        
        # 강의 생성
        course_data = {
            'course_name': '심화프로젝트랩',
            'professor_id': professor['user_id'],
            'professor_name': professor['name'],
            'enrolled_students': []
        }
        
        course_id = db.add_course(course_data)
        
        # 주차별 마감일 설정 (1~5주차)
        deadline = "2024-12-16T23:59:59"
        for week in range(1, 6):
            db.set_week_deadline(course_id, week, deadline)
        
        # 초대 링크 생성
        invitation_code = db.create_invitation(
            course_id=course_id,
            created_by=professor['user_id'],
            expires_at=None,
            max_uses=-1
        )
        
        return jsonify({
            'success': True,
            'message': '심화프로젝트랩 강의가 생성되었습니다!',
            'course_id': course_id,
            'invitation_code': invitation_code,
            'invitation_url': f'/invite/{invitation_code}'
        }), 201
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'강의 생성 실패: {str(e)}'
        }), 500

@api_course_bp.route('/<course_id>/invite', methods=['POST', 'OPTIONS'])
def create_invitation(course_id):
    """강의 초대 링크 생성 (교수만)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth(required_role='professor')
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    
    # 강의 확인
    course = db.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    if course['professor_id'] != user_id:
        return jsonify({'success': False, 'message': '본인의 강의만 접근할 수 있습니다.'}), 403
    
    data = request.get_json() or {}
    invitation_code = db.create_invitation(
        course_id=course_id,
        created_by=user_id,
        expires_at=data.get('expires_at'),
        max_uses=data.get('max_uses', -1)
    )
    
    return jsonify({
        'success': True,
        'invitation_code': invitation_code,
        'invitation_url': f'/invite/{invitation_code}'
    }), 201

@api_course_bp.route('/public-invitations', methods=['GET'])
def get_public_invitations():
    """공개 초대 코드 목록 (로그인 불필요)"""
    try:
        # 활성화된 모든 초대 코드 조회
        with db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT ci.invitation_code, ci.course_id, c.course_name, c.professor_name
                FROM course_invitations ci
                JOIN courses c ON ci.course_id = c.course_id
                WHERE ci.is_active = 1
                ORDER BY ci.created_at DESC
                LIMIT 5
            ''')
            rows = cursor.fetchall()
            
            invitations = []
            for row in rows:
                invitations.append({
                    'invitation_code': row['invitation_code'],
                    'course_name': row['course_name'],
                    'professor_name': row['professor_name']
                })
            
            return jsonify({
                'success': True,
                'invitations': invitations
            }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'invitations': []
        }), 200

@api_course_bp.route('/invite/<invitation_code>', methods=['GET'])
def get_invitation_info(invitation_code):
    """초대 링크 정보 조회"""
    invitation = db.get_invitation(invitation_code)
    
    if not invitation:
        return jsonify({'success': False, 'message': '유효하지 않은 초대 코드입니다.'}), 404
    
    course = db.get_course_by_id(invitation['course_id'])
    
    return jsonify({
        'success': True,
        'course': {
            'course_id': course['course_id'],
            'course_name': course['course_name'],
            'professor_name': course['professor_name']
        },
        'is_active': invitation['is_active'] == 1,
        'max_uses': invitation['max_uses'],
        'current_uses': invitation['current_uses']
    }), 200

@api_course_bp.route('/invite/<invitation_code>/join', methods=['POST', 'OPTIONS'])
def join_course_by_invitation(invitation_code):
    """초대 링크로 강의 참가"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth(required_role='student')
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    
    if db.use_invitation(invitation_code, user_id):
        invitation = db.get_invitation(invitation_code)
        course = db.get_course_by_id(invitation['course_id'])
        
        return jsonify({
            'success': True,
            'message': f'"{course["course_name"]}" 강의에 참가했습니다!',
            'course_id': course['course_id']
        }), 200
    else:
        return jsonify({
            'success': False,
            'message': '초대 링크가 만료되었거나 유효하지 않습니다.'
        }), 400

@api_course_bp.route('/<course_id>/week/<int:week>/deadline', methods=['POST', 'OPTIONS'])
def set_week_deadline(course_id, week):
    """주차별 업로드 마감일 설정 (교수만)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth(required_role='professor')
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    
    course = db.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    if course['professor_id'] != user_id:
        return jsonify({'success': False, 'message': '본인의 강의만 수정할 수 있습니다.'}), 403
    
    data = request.get_json()
    deadline = data.get('deadline')
    
    if not deadline:
        return jsonify({'success': False, 'message': '마감일을 입력해주세요.'}), 400
    
    db.set_week_deadline(course_id, week, deadline)
    
    return jsonify({
        'success': True,
        'message': f'{week}주차 업로드 마감일이 설정되었습니다.',
        'deadline': deadline
    }), 200

@api_course_bp.route('/<course_id>/week/<int:week>/create-custom', methods=['GET'])
def get_custom_pdf_materials(course_id, week):
    """나만의 PDF 제작용 자료 조회"""
    auth_result = check_auth(required_role='student')
    if auth_result:
        return auth_result
    
    course = db.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    # 마감일이 지나지 않았으면 접근 불가
    if not db.can_view_materials(course_id, week):
        deadline = db.get_week_deadline(course_id, week)
        deadline_str = deadline[:10] if deadline else "알 수 없음"
        return jsonify({
            'success': False, 
            'message': f'업로드 기간이 종료되어야 조합이 가능합니다. (마감일: {deadline_str})'
        }), 403
    
    materials = db.get_materials_by_course_week(course_id, week)
    student_materials = [m for m in materials if m['type'] == 'student']
    
    # 점수 순으로 정렬
    student_materials.sort(key=lambda x: (
        x.get('evaluation_score') is None,
        -(x.get('evaluation_score') or 0)
    ))
    
    return jsonify({
        'success': True,
        'course': course,
        'materials': student_materials
    }), 200
