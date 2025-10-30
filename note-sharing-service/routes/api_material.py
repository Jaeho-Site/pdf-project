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

@api_material_bp.route('/courses/<course_id>/week/<int:week>/upload', methods=['POST'])
def upload_material(course_id, week):
    """자료 업로드"""
    print("\n" + "=" * 70)
    print(f"[UPLOAD] 업로드 요청 받음")
    print(f"  - Course: {course_id}, Week: {week}")
    print(f"  - Session 존재 여부: {'user_id' in session}")
    
    if not require_login():
        print(f"  ❌ 로그인되지 않음!")
        print("=" * 70)
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session.get('user_id', 'UNKNOWN')
    role = session.get('role', 'UNKNOWN')
    name = session.get('name', 'UNKNOWN')
    
    print(f"  ✅ 세션에서 읽은 정보:")
    print(f"    - User ID: {user_id}")
    print(f"    - Name: {name}")
    print(f"    - Role: {role}")
    print(f"    - Session 전체: {dict(session)}")
    
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
    
    # role에 따라 분기 (중요!)
    if role == 'professor':
        result = file_service.save_professor_material(file, course_id, week, user_id)
        is_professor_material = True
        print(f"  📁 저장 타입: 교수 자료")
        print(f"  📂 저장 경로: storage/professor/{course_id}/week_{week}/")
    else:
        result = file_service.save_student_material(file, course_id, week, user_id)
        is_professor_material = False
        print(f"  📁 저장 타입: 학생 자료")
        print(f"  📂 저장 경로: storage/students/{user_id}/{course_id}/week_{week}/")
    
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
    
    print(f"  💾 저장할 material 데이터:")
    print(f"    - uploader_id: {material['uploader_id']}")
    print(f"    - uploader_name: {material['uploader_name']}")
    print(f"    - is_professor_material: {material['is_professor_material']}")
    print(f"    - file_name: {material['file_name']}")
    
    material_id = data_service.add_material(material)
    print(f"  ✅ 저장 완료! Material ID: {material_id}")
    
    # 썸네일 생성 (백그라운드)
    try:
        print(f"  🖼️  썸네일 생성 중...")
        thumbnail_paths = pdf_service.convert_pdf_to_images(file_path, material_id)
        print(f"  ✅ 썸네일 {len(thumbnail_paths)}개 생성 완료!")
    except Exception as e:
        print(f"  ⚠️  썸네일 생성 실패 (서비스는 정상 작동): {e}")
    
    print("=" * 70 + "\n")
    
    # 학생 업로드 시 알림 생성 (다른 학생들에게)
    if not is_professor_material:
        for student_id in course['enrolled_students']:
            if student_id != user_id:
                data_service.add_notification({
                    'user_id': student_id,
                    'course_id': course_id,
                    'message': f'{course["course_name"]} {week}주차 - {user["name"]}님이 필기를 업로드했습니다.'
                })
    
    return jsonify({
        'success': True,
        'message': f'"{filename}" 업로드 완료!',
        'material_id': material_id,
        'is_professor_material': is_professor_material
    }), 201

@api_material_bp.route('/materials/<material_id>/download', methods=['GET'])
def download_material(material_id):
    """자료 다운로드 (중복 방지: 세션 체크)"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 중복 다운로드 방지: 세션에 다운로드 기록 저장
    download_key = f"downloaded_{material_id}"
    if not session.get(download_key):
        data_service.increment_download_count(material_id)
        session[download_key] = True
        print(f"[DEBUG] 다운로드 카운트 증가: {material_id}, user: {user_id}")
    else:
        print(f"[DEBUG] 중복 다운로드 방지: {material_id}, user: {user_id}")
    
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
    
    return send_file(file_path, as_attachment=True, download_name=material['file_name'])

@api_material_bp.route('/materials/<material_id>/view', methods=['GET'])
def view_material(material_id):
    """자료 보기 (중복 방지: 세션 체크)"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    user_id = session['user_id']
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 중복 조회 방지: 세션에 조회 기록 저장
    view_key = f"viewed_{material_id}"
    if not session.get(view_key):
        data_service.increment_view_count(material_id)
        session[view_key] = True
        print(f"[DEBUG] 조회 카운트 증가: {material_id}, user: {user_id}")
    else:
        print(f"[DEBUG] 중복 조회 방지: {material_id}, user: {user_id}")
    
    file_path = material['file_path']
    
    if not os.path.exists(file_path):
        return jsonify({'success': False, 'message': '파일을 찾을 수 없습니다.'}), 404
    
    return send_file(file_path, mimetype='application/pdf')

@api_material_bp.route('/materials/<material_id>/thumbnails', methods=['GET'])
def get_material_thumbnails(material_id):
    """자료의 썸네일 목록 조회 (없으면 생성)"""
    if not require_login():
        return jsonify({'success': False, 'message': '로그인이 필요합니다.'}), 401
    
    material = data_service.get_material_by_id(material_id)
    
    if not material:
        return jsonify({'success': False, 'message': '존재하지 않는 자료입니다.'}), 404
    
    # 썸네일 경로 조회
    thumbnail_paths = pdf_service.get_thumbnail_paths(material_id)
    
    # 썸네일이 없으면 생성
    if not thumbnail_paths:
        print(f"[THUMBNAIL] {material_id} 썸네일 생성 중...")
        thumbnail_paths = pdf_service.convert_pdf_to_images(
            material['file_path'], 
            material_id
        )
    
    # 상대 경로로 변환 (API 경로)
    thumbnail_urls = [
        f"/api/storage/thumbnails/{material_id}/page_{i+1}.jpg"
        for i in range(len(thumbnail_paths))
    ]
    
    return jsonify({
        'success': True,
        'material_id': material_id,
        'thumbnail_count': len(thumbnail_urls),
        'thumbnails': thumbnail_urls
    }), 200
