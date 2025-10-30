# -*- coding: utf-8 -*-
"""
자료 업로드/다운로드 라우트
"""
from flask import Blueprint, request, redirect, url_for, flash, session, send_file
from services.data_service import DataService
from services.file_service import FileService
from services.pdf_service import PDFService
from utils.helpers import login_required, professor_required
import os

material_bp = Blueprint('material', __name__)
data_service = DataService()
file_service = FileService()
pdf_service = PDFService()

@material_bp.route('/courses/<course_id>/week/<int:week>/upload', methods=['POST'])
@login_required
def upload(course_id, week):
    """자료 업로드 (교수 또는 학생)"""
    user_id = session['user_id']
    role = session['role']
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        flash('존재하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 파일 확인
    if 'file' not in request.files:
        flash('파일을 선택해주세요.', 'warning')
        return redirect(url_for('course.week_materials', course_id=course_id, week=week))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('파일을 선택해주세요.', 'warning')
        return redirect(url_for('course.week_materials', course_id=course_id, week=week))
    
    if not file_service.allowed_file(file.filename):
        flash('PDF 파일만 업로드 가능합니다.', 'danger')
        return redirect(url_for('course.week_materials', course_id=course_id, week=week))
    
    # 역할에 따라 저장
    user = data_service.get_user_by_id(user_id)
    
    if role == 'professor':
        result = file_service.save_professor_material(file, course_id, week, user_id)
        is_professor_material = True
    else:
        result = file_service.save_student_material(file, course_id, week, user_id)
        is_professor_material = False
    
    if not result:
        flash('파일 업로드에 실패했습니다.', 'danger')
        return redirect(url_for('course.week_materials', course_id=course_id, week=week))
    
    file_path, filename = result
    
    # PDF 페이지 수 조회
    page_count = pdf_service.get_page_count(file_path)
    
    # 메타데이터 저장
    material = {
        'course_id': course_id,
        'week': week,
        'uploader_id': user_id,
        'uploader_name': user['name'],
        'is_professor_material': is_professor_material,
        'file_name': filename,
        'file_path': file_path,
        'page_count': page_count
    }
    
    material_id = data_service.add_material(material)
    
    # 학생이 필기를 업로드한 경우 알림 생성 (같은 강의 수강생에게)
    if not is_professor_material:
        for student_id in course['enrolled_students']:
            if student_id != user_id:  # 본인 제외
                data_service.add_notification({
                    'user_id': student_id,
                    'course_id': course_id,
                    'message': f'{course["course_name"]} {week}주차 PDF 필기 업로드 - {user["name"]}님이 필기를 업로드했습니다.'
                })
    
    flash(f'"{filename}" 업로드 완료!', 'success')
    return redirect(url_for('course.week_materials', course_id=course_id, week=week))

@material_bp.route('/materials/<material_id>/download')
@login_required
def download(material_id):
    """자료 다운로드"""
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        flash('존재하지 않는 자료입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 다운로드 수 증가
    data_service.increment_download_count(material_id)
    
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        flash('파일을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('main.index'))
    
    return send_file(file_path, 
                    as_attachment=True, 
                    download_name=material['file_name'])

@material_bp.route('/materials/<material_id>/view')
@login_required
def view(material_id):
    """자료 조회 (조회수 증가)"""
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        flash('존재하지 않는 자료입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 조회수 증가
    data_service.increment_view_count(material_id)
    
    # PDF를 바로 브라우저에서 보기
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        flash('파일을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('main.index'))
    
    return send_file(file_path, mimetype='application/pdf')

