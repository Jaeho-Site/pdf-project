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
    try:
        if not require_login():
            return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
        
        course = data_service.get_course_by_id(course_id)
        
        if not course:
            return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
        
        # 학생인 경우 마감일 체크 (열람 가능 여부)
        role = session.get('role')
        can_view = True
        if role == 'student':
            try:
                can_view = data_service.can_view_materials(course_id, week)
            except Exception as e:
                print(f"[ERROR] can_view_materials 오류: {e}")
                import traceback
                traceback.print_exc()
                # 오류 발생 시 안전하게 True로 설정
                can_view = True
        
        materials = data_service.get_materials_by_course_week(course_id, week)
        
        professor_materials = [m for m in materials if m['is_professor_material']]
        student_materials = [m for m in materials if not m['is_professor_material']]
        
        # 학생 자료는 마감일이 지나지 않았으면 숨김 (교수는 항상 볼 수 있음)
        # 단, 본인이 업로드한 자료는 항상 볼 수 있음
        if role == 'student' and not can_view:
            user_id = session.get('user_id')
            # 본인이 업로드한 자료만 필터링
            student_materials = [m for m in student_materials if m.get('uploader_id') == user_id]
        
        # 정렬 (점수 순 추가)
        sort_by = request.args.get('sort', 'latest')
        if sort_by == 'name':
            student_materials.sort(key=lambda x: x.get('uploader_name', ''))
        elif sort_by == 'popular':
            student_materials.sort(key=lambda x: x.get('view_count', 0), reverse=True)
        elif sort_by == 'downloads':
            student_materials.sort(key=lambda x: x.get('download_count', 0), reverse=True)
        elif sort_by == 'score':
            # 점수 순 정렬 (점수가 없는 것은 뒤로)
            student_materials.sort(key=lambda x: (
                x.get('quality_score') is None,
                -(x.get('quality_score') or 0)
            ))
        else:
            student_materials.sort(key=lambda x: x.get('upload_date', ''), reverse=True)
        
        # 마감일 정보 추가
        deadline = None
        evaluation_status = None
        try:
            deadline = data_service.get_week_deadline(course_id, week)
            weeks_config = course.get('weeks', {})
            week_str = str(week)
            if week_str in weeks_config:
                evaluation_status = weeks_config[week_str].get('evaluation_status', 'pending')
        except Exception as e:
            print(f"[ERROR] 마감일 정보 조회 오류: {e}")
            import traceback
            traceback.print_exc()
        
        # can_upload: 교수는 항상 true, 학생은 마감일 체크
        can_upload = True
        if role == 'student':
            try:
                can_upload = data_service.is_upload_period_open(course_id, week)
            except Exception as e:
                print(f"[ERROR] is_upload_period_open 오류: {e}")
                import traceback
                traceback.print_exc()
                # 오류 발생 시 안전하게 True로 설정
                can_upload = True
        
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
        print(f"[ERROR] get_week_materials 전체 오류: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'자료 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500

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

@api_course_bp.route('/<course_id>/week/<int:week>/deadline', methods=['POST'])
def set_week_deadline(course_id, week):
    """주차별 업로드 마감일 설정 (교수만)"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'professor':
        return jsonify({'success': False, 'message': '교수만 접근할 수 있습니다.'}), 403
    
    course = data_service.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    if course['professor_id'] != session['user_id']:
        return jsonify({'success': False, 'message': '본인의 강의만 수정할 수 있습니다.'}), 403
    
    data = request.get_json()
    deadline = data.get('deadline')
    
    if not deadline:
        return jsonify({'success': False, 'message': '마감일을 입력해주세요.'}), 400
    
    data_service.set_week_deadline(course_id, week, deadline)
    
    return jsonify({
        'success': True,
        'message': f'{week}주차 업로드 마감일이 설정되었습니다.',
        'deadline': deadline
    }), 200

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
    
    # 마감일이 지나지 않았으면 접근 불가
    if not data_service.can_view_materials(course_id, week):
        deadline = data_service.get_week_deadline(course_id, week)
        deadline_str = deadline[:10] if deadline else "알 수 없음"
        return jsonify({
            'success': False, 
            'message': f'업로드 기간이 종료되어야 조합이 가능합니다. (마감일: {deadline_str})'
        }), 403
    
    materials = data_service.get_materials_by_course_week(course_id, week)
    student_materials = [m for m in materials if not m['is_professor_material']]
    
    # 점수 순으로 정렬 (점수가 없는 것은 뒤로)
    student_materials.sort(key=lambda x: (
        x.get('quality_score') is None,
        -(x.get('quality_score') or 0)
    ))
    
    return jsonify({
        'success': True,
        'course': course,
        'materials': student_materials
    }), 200

