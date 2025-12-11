# -*- coding: utf-8 -*-
"""
API 자료 업로드/다운로드 라우트 (SQLite + GCS 버전)
"""
from flask import Blueprint, request, jsonify, session, send_file
from services.database_service import DatabaseService
from services.gcs_storage_service import GCSStorageService
from services.pdf_service import PDFService
import os
import tempfile

api_material_bp = Blueprint('api_material', __name__)
db = DatabaseService()
storage = GCSStorageService()
pdf_service = PDFService()

def require_login():
    """로그인 확인"""
    if 'user_id' not in session:
        return False
    return True

@api_material_bp.route('/courses/<course_id>/week/<int:week>/upload', methods=['POST'])
def upload_material(course_id, week):
    """자료 업로드"""
    print("\n" + "=" * 70)
    print(f"[UPLOAD] 업로드 요청 받음")
    print(f"  - Course: {course_id}, Week: {week}")
    
    if not require_login():
        print(f"  ❌ 로그인되지 않음!")
        print("=" * 70)
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session.get('user_id')
    role = session.get('role')
    name = session.get('name')
    
    print(f"  ✅ 세션 정보:")
    print(f"    - User ID: {user_id}")
    print(f"    - Name: {name}")
    print(f"    - Role: {role}")
    
    course = db.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    # 학생 업로드인 경우 마감일 체크
    if role == 'student':
        if not db.is_upload_period_open(course_id, week):
            deadline = db.get_week_deadline(course_id, week)
            deadline_str = deadline[:10] if deadline else "알 수 없음"
            return jsonify({
                'success': False, 
                'message': f'업로드 기간이 종료되었습니다. (마감일: {deadline_str})'
            }), 403
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'message': '파일을 선택해주세요.'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'success': False, 'message': '파일을 선택해주세요.'}), 400
    
    if not storage.allowed_file(file.filename):
        return jsonify({'success': False, 'message': 'PDF 파일만 업로드 가능합니다.'}), 400
    
    user = db.get_user_by_id(user_id)
    
    # role에 따라 분기
    if role == 'professor':
        result = storage.save_professor_material(file, course_id, week, user_id)
        mat_type = 'professor'
        print(f"  📁 저장 타입: 교수 자료")
        print(f"  📂 GCS 경로: storage/professor/{course_id}/week_{week}/")
    else:
        result = storage.save_student_material(file, course_id, week, user_id)
        mat_type = 'student'
        print(f"  📁 저장 타입: 학생 자료")
        print(f"  📂 GCS 경로: storage/students/{user_id}/{course_id}/week_{week}/")
    
    if not result:
        return jsonify({'success': False, 'message': '파일 업로드에 실패했습니다.'}), 500
    
    gcs_path, filename = result
    print(f"  ✅ GCS 업로드 성공: {gcs_path}")
    
    # PDF 페이지 수 확인 (GCS에서 임시 다운로드)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    try:
        pdf_data = storage.download_to_memory(gcs_path)
        if pdf_data:
            temp_file.write(pdf_data)
            temp_file.close()
            page_count = pdf_service.get_page_count(temp_file.name)
            print(f"  📄 페이지 수: {page_count}")
        else:
            page_count = 0
            print(f"  ⚠️ 페이지 수 확인 실패")
    finally:
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
    
    material = {
        'course_id': course_id,
        'week': week,
        'uploader_id': user_id,
        'uploader_name': user['name'],
        'type': mat_type,
        'filename': filename,
        'gcs_path': gcs_path,
        'page_count': page_count
    }
    
    material_id = db.add_material(material)
    print(f"  ✅ DB 저장 완료! Material ID: {material_id}")
    
    # 썸네일 생성 (백그라운드, GCS에 저장)
    try:
        print(f"  🖼️  썸네일 생성 중...")
        thumbnail_paths = pdf_service.convert_pdf_to_images_from_gcs(gcs_path, material_id, storage)
        print(f"  ✅ 썸네일 {len(thumbnail_paths)}개 GCS 업로드 완료!")
    except Exception as e:
        print(f"  ⚠️  썸네일 생성 실패 (서비스는 정상 작동): {e}")
    
    print("=" * 70 + "\n")
    
    # 학생 업로드 시 알림 생성
    if mat_type == 'student':
        for student_id in course['enrolled_students']:
            if student_id != user_id:
                db.add_notification({
                    'user_id': student_id,
                    'type': 'material_upload',
                    'related_id': material_id,
                    'message': f'{course["course_name"]} {week}주차 - {user["name"]}님이 필기를 업로드했습니다.'
                })
    
    return jsonify({
        'success': True,
        'message': f'"{filename}" 업로드 완료!',
        'material_id': material_id,
        'type': mat_type
    }), 201

@api_material_bp.route('/materials/<material_id>/download', methods=['GET'])
def download_material(material_id):
    """자료 다운로드"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    material = db.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 중복 다운로드 방지
    download_key = f"downloaded_{material_id}"
    if not session.get(download_key):
        db.increment_download_count(material_id)
        session[download_key] = True
        print(f"[DEBUG] 다운로드 카운트 증가: {material_id}, user: {user_id}")
    else:
        print(f"[DEBUG] 중복 다운로드 방지: {material_id}, user: {user_id}")
    
    # GCS에서 임시 다운로드
    gcs_path = material['gcs_path']
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    try:
        if storage.download_file(gcs_path, temp_file.name):
            return send_file(
                temp_file.name,
                as_attachment=True,
                download_name=material['filename']
            )
        else:
            return jsonify({'success': False, 'message': 'GCS 다운로드 실패'}), 500
    except Exception as e:
        print(f"[ERROR] 다운로드 오류: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return jsonify({'success': False, 'message': f'다운로드 오류: {str(e)}'}), 500

@api_material_bp.route('/materials/<material_id>/view', methods=['GET'])
def view_material(material_id):
    """자료 보기"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    material = db.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 중복 조회 방지
    view_key = f"viewed_{material_id}"
    if not session.get(view_key):
        db.increment_view_count(material_id)
        session[view_key] = True
        print(f"[DEBUG] 조회 카운트 증가: {material_id}, user: {user_id}")
    else:
        print(f"[DEBUG] 중복 조회 방지: {material_id}, user: {user_id}")
    
    # GCS에서 임시 다운로드
    gcs_path = material['gcs_path']
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
    
    try:
        if storage.download_file(gcs_path, temp_file.name):
            return send_file(temp_file.name, mimetype='application/pdf')
        else:
            return jsonify({'success': False, 'message': 'GCS 다운로드 실패'}), 500
    except Exception as e:
        print(f"[ERROR] 조회 오류: {e}")
        if os.path.exists(temp_file.name):
            os.unlink(temp_file.name)
        return jsonify({'success': False, 'message': f'조회 오류: {str(e)}'}), 500

@api_material_bp.route('/materials/<material_id>/thumbnails', methods=['GET'])
def get_material_thumbnails(material_id):
    """자료의 썸네일 목록 조회"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    material = db.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 썸네일 GCS 경로 확인
    thumbnail_prefix = f"storage/thumbnails/{material_id}/"
    thumbnail_files = storage.list_files(thumbnail_prefix)
    
    # 썸네일이 없으면 생성
    if not thumbnail_files:
        print(f"[THUMBNAIL] {material_id} 썸네일 생성 중...")
        try:
            thumbnail_files = pdf_service.convert_pdf_to_images_from_gcs(
                material['gcs_path'], 
                material_id,
                storage
            )
        except Exception as e:
            print(f"[ERROR] 썸네일 생성 실패: {e}")
            return jsonify({'success': False, 'message': '썸네일 생성 실패'}), 500
    
    # GCS Signed URL 생성 (1시간 유효)
    thumbnail_urls = []
    for gcs_path in thumbnail_files:
        signed_url = storage.get_signed_url(gcs_path, expiration=3600)
        if signed_url:
            thumbnail_urls.append(signed_url)
    
    return jsonify({
        'success': True,
        'material_id': material_id,
        'thumbnail_count': len(thumbnail_urls),
        'thumbnails': thumbnail_urls
    }), 200
