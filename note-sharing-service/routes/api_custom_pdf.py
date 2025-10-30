# -*- coding: utf-8 -*-
"""
API 나만의 PDF 라우트 (JSON 응답)
"""
from flask import Blueprint, request, jsonify, session, send_file
from services.data_service import DataService
from services.pdf_service import PDFService
from services.file_service import FileService
import os

api_custom_pdf_bp = Blueprint('api_custom_pdf', __name__)
data_service = DataService()
pdf_service = PDFService()
file_service = FileService()

def require_login():
    """로그인 확인"""
    if 'user_id' not in session:
        return False
    return True

@api_custom_pdf_bp.route('/<course_id>/week/<int:week>/generate-custom', methods=['POST'])
def generate_custom_pdf(course_id, week):
    """나만의 PDF 생성"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    user = data_service.get_user_by_id(user_id)
    course = data_service.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    data = request.get_json()
    selected_pages = data.get('selected_pages', [])
    
    if not selected_pages:
        return jsonify({'success': False, 'message': '선택된 페이지가 없습니다.'}), 400
    
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
    
    temp_output_path = os.path.join(
        pdf_service.storage_dir,
        'temp',
        f'custom_{user_id}_{course_id}_week{week}.pdf'
    )
    
    success = pdf_service.create_custom_pdf(page_selections, temp_output_path)
    
    if not success:
        return jsonify({'success': False, 'message': 'PDF 생성에 실패했습니다.'}), 500
    
    custom_pdf = {
        'student_id': user_id,
        'student_name': user['name'],
        'course_id': course_id,
        'week': week,
        'file_name': f'{user["name"]}_나만의필기_{course["course_name"]}_week{week}.pdf',
        'file_path': '',
        'page_selections': page_info_list
    }
    
    custom_pdf_id = data_service.add_custom_pdf(custom_pdf)
    
    final_path = file_service.save_custom_pdf(temp_output_path, user_id, custom_pdf_id)
    
    if not final_path:
        return jsonify({'success': False, 'message': '파일 저장에 실패했습니다.'}), 500
    
    # JSON 파일 업데이트
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
    
    if os.path.exists(temp_output_path):
        os.remove(temp_output_path)
    
    return jsonify({
        'success': True,
        'message': 'PDF가 생성되었습니다!',
        'custom_pdf_id': custom_pdf_id
    }), 201

@api_custom_pdf_bp.route('/my-list', methods=['GET'])
def get_my_custom_pdfs():
    """내 나만의 PDF 목록"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    custom_pdfs = data_service.get_custom_pdfs_by_student(user_id)
    
    for cp in custom_pdfs:
        course = data_service.get_course_by_id(cp['course_id'])
        cp['course_name'] = course['course_name'] if course else '알 수 없음'
    
    return jsonify({
        'success': True,
        'custom_pdfs': custom_pdfs
    }), 200

@api_custom_pdf_bp.route('/<custom_pdf_id>/download', methods=['GET'])
def download_custom_pdf(custom_pdf_id):
    """나만의 PDF 다운로드"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    custom_pdf = data_service.get_custom_pdf_by_id(custom_pdf_id)
    
    if not custom_pdf:
        return jsonify({'success': False, 'message': '존재하지 않는 파일입니다.'}), 404
    
    if custom_pdf['student_id'] != user_id:
        return jsonify({'success': False, 'message': '본인의 파일만 다운로드할 수 있습니다.'}), 403
    
    file_path = custom_pdf['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=custom_pdf['file_name'])

