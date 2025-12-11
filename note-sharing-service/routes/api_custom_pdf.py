# -*- coding: utf-8 -*-
"""
API 나만의 PDF 라우트 (SQLite + GCS 버전)
"""
from flask import Blueprint, request, jsonify, session, send_file
from services.database_service import DatabaseService
from services.gcs_storage_service import GCSStorageService
from utils.auth_middleware import check_auth
from PyPDF2 import PdfReader, PdfWriter
import os
import tempfile
from io import BytesIO

api_custom_pdf_bp = Blueprint('api_custom_pdf', __name__)
db = DatabaseService()
storage = GCSStorageService()

def require_login():
    """로그인 확인"""
    return check_auth()

@api_custom_pdf_bp.route('/courses/<course_id>/week/<int:week>/generate-custom', methods=['POST'])
def generate_custom_pdf(course_id, week):
    """나만의 PDF 생성"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    user = db.get_user_by_id(user_id)
    course = db.get_course_by_id(course_id)
    
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    data = request.get_json()
    selected_pages = data.get('selected_pages', [])
    
    if not selected_pages:
        return jsonify({'success': False, 'message': '선택된 페이지가 없습니다.'}), 400
    
    print(f"[CUSTOM PDF] {len(selected_pages)}개 페이지 병합 시작...")
    
    # PDF Writer 생성
    writer = PdfWriter()
    page_info_list = []
    
    # 각 페이지 추출 및 병합
    for selection in selected_pages:
        material_id = selection['material_id']
        page_num = selection['page_num']
        
        material = db.get_material_by_id(material_id)
        
        if not material:
            continue
        
        # GCS에서 임시 다운로드
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        try:
            print(f"  📥 다운로드 중: {material_id} (페이지 {page_num})")
            if storage.download_file(material['gcs_path'], temp_pdf.name):
                # PDF 페이지 추출
                reader = PdfReader(temp_pdf.name)
                writer.add_page(reader.pages[page_num - 1])  # 1-based → 0-based
                
                page_info_list.append({
                    'material_id': material_id,
                    'page_number': page_num
                })
        except Exception as e:
            print(f"  ⚠️ 페이지 추출 실패: {e}")
        finally:
            if os.path.exists(temp_pdf.name):
                os.unlink(temp_pdf.name)
    
    if not page_info_list:
        return jsonify({'success': False, 'message': 'PDF 생성 실패'}), 500
    
    # 메모리에 PDF 저장
    output_buffer = BytesIO()
    writer.write(output_buffer)
    pdf_bytes = output_buffer.getvalue()
    
    print(f"  ✅ PDF 병합 완료 ({len(pdf_bytes)} bytes)")
    
    # GCS에 저장
    custom_pdf_data = {
        'student_id': user_id,
        'course_id': course_id,
        'week': week,
        'title': f'{user["name"]}_나만의필기_{course["course_name"]}_week{week}.pdf',
        'page_count': len(page_info_list),
        'selected_pages': page_info_list
    }
    
    custom_pdf_id = db.add_custom_pdf(custom_pdf_data)
    
    # GCS에 업로드
    gcs_path = storage.save_custom_pdf(pdf_bytes, user_id, custom_pdf_id)
    
    if not gcs_path:
        return jsonify({'success': False, 'message': '파일 저장 실패'}), 500
    
    # DB 업데이트 (gcs_path 저장)
    with db.get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE custom_pdfs
            SET gcs_path = ?
            WHERE custom_pdf_id = ?
        ''', (gcs_path, custom_pdf_id))
    
    print(f"  ✅ GCS 업로드 완료: {gcs_path}")
    
    return jsonify({
        'success': True,
        'message': 'PDF가 생성되었습니다!',
        'custom_pdf_id': custom_pdf_id
    }), 201

@api_custom_pdf_bp.route('/custom-pdfs/my-list', methods=['GET'])
def get_my_custom_pdfs():
    """내 나만의 PDF 목록"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    custom_pdfs = db.get_custom_pdfs_by_student(user_id)
    
    for cp in custom_pdfs:
        course = db.get_course_by_id(cp['course_id'])
        cp['course_name'] = course['course_name'] if course else '알 수 없음'
    
    return jsonify({
        'success': True,
        'custom_pdfs': custom_pdfs
    }), 200

@api_custom_pdf_bp.route('/custom-pdfs/<custom_pdf_id>/download', methods=['GET'])
def download_custom_pdf(custom_pdf_id):
    """나만의 PDF 다운로드"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    if session.get('role') != 'student':
        return jsonify({'success': False, 'message': '학생만 접근할 수 있습니다.'}), 403
    
    user_id = session['user_id']
    custom_pdf = db.get_custom_pdf_by_id(custom_pdf_id)
    
    if not custom_pdf:
        return jsonify({'success': False, 'message': '존재하지 않는 파일입니다.'}), 404
    
    if custom_pdf['student_id'] != user_id:
        return jsonify({'success': False, 'message': '본인의 파일만 다운로드할 수 있습니다.'}), 403
    
    # GCS에서 임시 다운로드
    gcs_path = custom_pdf['gcs_path']
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    try:
        if storage.download_file(gcs_path, temp_file.name):
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=custom_pdf['title']
            )
        else:
            return jsonify({'success': False, 'message': 'GCS 다운로드 실패'}), 500
    except Exception as e:
        print(f"[ERROR] 다운로드 오류: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return jsonify({'success': False, 'message': f'다운로드 오류: {str(e)}'}), 500
