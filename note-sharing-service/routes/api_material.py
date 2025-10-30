# -*- coding: utf-8 -*-
"""
API 자료 업로드/다운로드 라우트 (JSON 응답)
"""
from flask import Blueprint, request, jsonify, session, send_file
from services.data_service import DataService
from services.file_service import FileService
from services.pdf_service import PDFService
import os

api_material_bp = Blueprint('api_material', __name__)
data_service = DataService()
file_service = FileService()
pdf_service = PDFService()

def require_login():
    """로그인 확인"""
    if 'user_id' not in session:
        return False
    return True

@api_material_bp.route('/<course_id>/week/<int:week>/upload', methods=['POST'])
def upload_material(course_id, week):
    """자료 업로드"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    role = session['role']
    
    course = data_service.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일을 선택해주세요.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일을 선택해주세요.'}), 400
    
    if not file_service.allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'PDF 파일만 업로드 가능합니다.'}), 400
    
    user = data_service.get_user_by_id(user_id)
    
    if role == 'professor':
        result = file_service.save_professor_material(file, course_id, week, user_id)
        is_professor_material = True
    else:
        result = file_service.save_student_material(file, course_id, week, user_id)
        is_professor_material = False
    
    if not result:
        return jsonify({'success': False, 'message': '파일 업로드에 실패했습니다.'}), 500
    
    file_path, filename = result
    page_count = pdf_service.get_page_count(file_path)
    
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
    
    # 학생 업로드 시 알림 생성
    if not is_professor_material:
        for student_id in course['enrolled_students']:
            if student_id != user_id:
                data_service.add_notification({
                    'user_id': student_id,
                    'course_id': course_id,
                    'message': f'{course["course_name"]} {week}주차 PDF 필기 업로드 - {user["name"]}님이 필기를 업로드했습니다.'
                })
    
    return jsonify({
        'success': True,
        'message': f'"{filename}" 업로드 완료!',
        'material_id': material_id
    }), 201

@api_material_bp.route('/<material_id>/download', methods=['GET'])
def download_material(material_id):
    """자료 다운로드"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    data_service.increment_download_count(material_id)
    
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=material['file_name'])

@api_material_bp.route('/<material_id>/view', methods=['GET'])
def view_material(material_id):
    """자료 보기"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    data_service.increment_view_count(material_id)
    
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
    
    return send_file(file_path, mimetype='application/pdf')

