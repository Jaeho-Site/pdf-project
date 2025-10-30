# -*- coding: utf-8 -*-
"""
API 강의 라우트 (JSON 응답)
"""
from flask import Blueprint, request, jsonify, session
from services.data_service import DataService

api_course_bp = Blueprint('api_course', __name__)
data_service = DataService()

def require_login():
    """로그인 확인"""
    if 'user_id' not in session:
        return False
    return True

@api_course_bp.route('', methods=['GET'])
def get_courses():
    """강의 목록 조회"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    role = session['role']
    
    if role == 'professor':
        courses = data_service.get_courses_by_professor(user_id)
    else:
        courses = data_service.get_courses_by_student(user_id)
    
    return jsonify({
        'success': True,
        'courses': courses
    }), 200

@api_course_bp.route('/<course_id>', methods=['GET'])
def get_course_detail(course_id):
    """강의 상세 조회"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    # 주차별 자료 통계
    weeks_data = []
    for week in range(1, 17):
        materials = data_service.get_materials_by_course_week(course_id, week)
        professor_materials = [m for m in materials if m['is_professor_material']]
        student_materials = [m for m in materials if not m['is_professor_material']]
        
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
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    materials = data_service.get_materials_by_course_week(course_id, week)
    
    professor_materials = [m for m in materials if m['is_professor_material']]
    student_materials = [m for m in materials if not m['is_professor_material']]
    
    # 정렬
    sort_by = request.args.get('sort', 'latest')
    if sort_by == 'name':
        student_materials.sort(key=lambda x: x['uploader_name'])
    elif sort_by == 'popular':
        student_materials.sort(key=lambda x: x['view_count'], reverse=True)
    elif sort_by == 'downloads':
        student_materials.sort(key=lambda x: x['download_count'], reverse=True)
    else:
        student_materials.sort(key=lambda x: x['upload_date'], reverse=True)
    
    return jsonify({
        'success': True,
        'course': course,
        'professor_materials': professor_materials,
        'student_materials': student_materials
    }), 200

@api_course_bp.route('/create', methods=['POST'])
def create_course():
    """강의 생성 (교수만)"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'professor':
        return jsonify({'success': False, 'message': '교수만 접근할 수 있습니다.'}), 403
    
    data = request.get_json()
    professor_id = session['user_id']
    professor = data_service.get_user_by_id(professor_id)
    
    course = {
        'course_name': data.get('course_name'),
        'professor_id': professor_id,
        'professor_name': professor['name'],
        'year': int(data.get('year')),
        'semester': int(data.get('semester')),
        'enrolled_students': []
    }
    
    course_id = data_service.add_course(course)
    
    return jsonify({
        'success': True,
        'message': f'강의 "{course["course_name"]}"이(가) 생성되었습니다.',
        'course_id': course_id
    }), 201

@api_course_bp.route('/<course_id>/week/<int:week>/create-custom', methods=['GET'])
def get_custom_pdf_materials(course_id, week):
    """나만의 PDF 제작용 자료 조회"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    materials = data_service.get_materials_by_course_week(course_id, week)
    student_materials = [m for m in materials if not m['is_professor_material']]
    
    return jsonify({
        'success': True,
        'course': course,
        'materials': student_materials
    }), 200

