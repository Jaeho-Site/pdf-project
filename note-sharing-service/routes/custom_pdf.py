# -*- coding: utf-8 -*-
"""
나만의 PDF 제작 라우트
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, send_file
from services.data_service import DataService
from services.pdf_service import PDFService
from services.file_service import FileService
from utils.helpers import login_required, student_required
import os

custom_pdf_bp = Blueprint('custom_pdf', __name__)
data_service = DataService()
pdf_service = PDFService()
file_service = FileService()

@custom_pdf_bp.route('/courses/<course_id>/week/<int:week>/create-custom')
@student_required
def create_page(course_id, week):
    """나만의 PDF 제작 페이지"""
    user_id = session['user_id']
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        flash('존재하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 접근 권한 확인
    if user_id not in course['enrolled_students']:
        flash('수강하지 않는 강의입니다.', 'danger')
        return redirect(url_for('main.index'))
    
    # 해당 주차의 모든 자료 조회
    materials = data_service.get_materials_by_course_week(course_id, week)
    
    # 학생 필기만 (교수 자료 제외)
    student_materials = [m for m in materials if not m['is_professor_material']]
    
    if not student_materials:
        flash('아직 업로드된 학생 필기가 없습니다.', 'warning')
        return redirect(url_for('course.week_materials', course_id=course_id, week=week))
    
    # 각 자료의 PDF를 이미지로 변환
    materials_with_images = []
    
    for material in student_materials:
        # 이미지 변환 (캐싱됨)
        image_paths = pdf_service.convert_pdf_to_images(
            material['file_path'],
            material['material_id']
        )
        
        material['image_paths'] = image_paths
        material['page_count'] = len(image_paths)
        materials_with_images.append(material)
    
    return render_template('create_custom_pdf.html',
                         course=course,
                         week=week,
                         materials=materials_with_images)

@custom_pdf_bp.route('/courses/<course_id>/week/<int:week>/generate-custom', methods=['POST'])
@student_required
def generate(course_id, week):
    """나만의 PDF 생성"""
    user_id = session['user_id']
    user = data_service.get_user_by_id(user_id)
    
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    # 선택된 페이지 정보 받기
    # 형식: [{"material_id": "M001", "page_num": 1}, ...]
    selected_pages = request.json.get('selected_pages', [])
    
    if not selected_pages:
        return jsonify({'success': False, 'message': '선택된 페이지가 없습니다.'}), 400
    
    # 페이지 선택 정보 구성
    page_selections = []
    page_info_list = []
    
    for selection in selected_pages:
        material_id = selection['material_id']
        page_num = selection['page_num']
        
        material = data_service.get_material_by_id(material_id)
        
        if not material:
            continue
        
        page_selections.append({
            'source_material_id': material_id,
            'source_pdf_path': material['file_path'],
            'page_num': page_num
        })
        
        page_info_list.append({
            'page_num': page_num,
            'source_material_id': material_id,
            'source_student_id': material['uploader_id'],
            'source_student_name': material['uploader_name']
        })
    
    # 임시 출력 경로
    temp_output_path = os.path.join(
        pdf_service.storage_dir,
        'temp',
        f'custom_{user_id}_{course_id}_week{week}.pdf'
    )
    
    # PDF 생성
    success = pdf_service.create_custom_pdf(page_selections, temp_output_path)
    
    if not success:
        return jsonify({'success': False, 'message': 'PDF 생성에 실패했습니다.'}), 500
    
    # 메타데이터 저장
    custom_pdf = {
        'student_id': user_id,
        'student_name': user['name'],
        'course_id': course_id,
        'week': week,
        'file_name': f'{user["name"]}_나만의필기_{course["course_name"]}_week{week}.pdf',
        'file_path': '',  # 아래에서 설정
        'page_selections': page_info_list
    }
    
    custom_pdf_id = data_service.add_custom_pdf(custom_pdf)
    
    # 최종 저장 경로로 이동
    final_path = file_service.save_custom_pdf(temp_output_path, user_id, custom_pdf_id)
    
    if not final_path:
        return jsonify({'success': False, 'message': '파일 저장에 실패했습니다.'}), 500
    
    # 파일 경로 업데이트
    custom_pdf_data = data_service.get_custom_pdf_by_id(custom_pdf_id)
    custom_pdf_data['file_path'] = final_path
    
    # JSON 파일 직접 업데이트
    import json
    json_path = data_service.files['custom_pdfs']
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    for cp in data['custom_pdfs']:
        if cp['custom_pdf_id'] == custom_pdf_id:
            cp['file_path'] = final_path
            break
    
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    # 임시 파일 삭제
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)
    
    return jsonify({
        'success': True, 
        'message': 'PDF가 생성되었습니다!',
        'custom_pdf_id': custom_pdf_id
    })

@custom_pdf_bp.route('/my-custom-pdfs')
@student_required
def my_list():
    """내가 만든 나만의 PDF 목록"""
    user_id = session['user_id']
    
    custom_pdfs = data_service.get_custom_pdfs_by_student(user_id)
    
    # 강의 정보 추가
    for cp in custom_pdfs:
        course = data_service.get_course_by_id(cp['course_id'])
        cp['course_name'] = course['course_name'] if course else '알 수 없음'
    
    return render_template('my_custom_pdfs.html', custom_pdfs=custom_pdfs)

@custom_pdf_bp.route('/custom-pdfs/<custom_pdf_id>/download')
@student_required
def download(custom_pdf_id):
    """나만의 PDF 다운로드"""
    user_id = session['user_id']
    
    custom_pdf = data_service.get_custom_pdf_by_id(custom_pdf_id)
    
    if not custom_pdf:
        flash('존재하지 않는 파일입니다.', 'danger')
        return redirect(url_for('custom_pdf.my_list'))
    
    # 본인 파일만 다운로드 가능
    if custom_pdf['student_id'] != user_id:
        flash('본인의 파일만 다운로드할 수 있습니다.', 'danger')
        return redirect(url_for('custom_pdf.my_list'))
    
    file_path = custom_pdf['file_path']
    
    if not os.path.exists(file_path):
        flash('파일을 찾을 수 없습니다.', 'danger')
        return redirect(url_for('custom_pdf.my_list'))
    
    return send_file(file_path,
                    as_attachment=True,
                    download_name=custom_pdf['file_name'])

