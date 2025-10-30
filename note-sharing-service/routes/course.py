# -*- coding: utf-8 -*-
"""
강의/자료실 관련 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from services.data_service import DataService
from utils.helpers import login_required, professor_required

course_bp = Blueprint('course', __name__)
data_service = DataService()

@course_bp.route('/courses/<course_id>')
@login_required
def detail(course_id):
    """강의 상세 페이지 (주차별 폴더)"""
    user_id = session['user_id']
    role = session['role']
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        flash('존재하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 접근 권한 확인
    if role == 'student' and user_id not in course['enrolled_students']:
        flash('수강하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    if role == 'professor' and course['professor_id'] != user_id:
        flash('담당하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 주차별 자료 통계 (1~16주차)
    weeks_data = []
    for week in range(1, 17):
        materials = data_service.get_materials_by_course_week(course_id, week)
        
        # 교수 자료와 학생 필기 분리
        professor_materials = [m for m in materials if m['is_professor_material']]
        student_materials = [m for m in materials if not m['is_professor_material']]
        
        weeks_data.append({
            'week': week,
            'professor_count': len(professor_materials),
            'student_count': len(student_materials),
            'total_downloads': sum(m['download_count'] for m in materials),
            'total_views': sum(m['view_count'] for m in materials)
        })
    
    return render_template('course_detail.html', 
                         course=course,
                         weeks_data=weeks_data)

@course_bp.route('/courses/<course_id>/week/<int:week>')
@login_required
def week_materials(course_id, week):
    """주차별 자료 목록"""
    user_id = session['user_id']
    role = session['role']
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        flash('존재하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 접근 권한 확인
    if role == 'student' and user_id not in course['enrolled_students']:
        flash('수강하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 자료 목록 조회
    materials = data_service.get_materials_by_course_week(course_id, week)
    
    # 교수 자료와 학생 필기 분리
    professor_materials = [m for m in materials if m['is_professor_material']]
    student_materials = [m for m in materials if not m['is_professor_material']]
    
    # 정렬 옵션
    sort_by = request.args.get('sort', 'latest')  # latest, name, popular, downloads
    
    if sort_by == 'name':
        student_materials.sort(key=lambda x: x['uploader_name'])
    elif sort_by == 'popular':
        student_materials.sort(key=lambda x: x['view_count'], reverse=True)
    elif sort_by == 'downloads':
        student_materials.sort(key=lambda x: x['download_count'], reverse=True)
    else:  # latest
        student_materials.sort(key=lambda x: x['upload_date'], reverse=True)
    
    return render_template('week_material.html',
                         course=course,
                         week=week,
                         professor_materials=professor_materials,
                         student_materials=student_materials,
                         sort_by=sort_by)

@course_bp.route('/courses/create', methods=['GET', 'POST'])
@professor_required
def create():
    """자료실 생성 (교수만)"""
    if request.method == 'POST':
        course_name = request.form.get('course_name')
        year = int(request.form.get('year'))
        semester = int(request.form.get('semester'))
        
        professor_id = session['user_id']
        professor = data_service.get_user_by_id(professor_id)
        
        course = {
            'course_name': course_name,
            'professor_id': professor_id,
            'professor_name': professor['name'],
            'year': year,
            'semester': semester,
            'enrolled_students': []
        }
        
        course_id = data_service.add_course(course)
        
        flash(f'강의 "{course_name}"이(가) 생성되었습니다.', 'success')
        return redirect(url_for('course.detail', course_id=course_id))
    
    return render_template('course_create.html')

