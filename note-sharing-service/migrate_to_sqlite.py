# -*- coding: utf-8 -*-
"""
JSON 파일을 SQLite로 마이그레이션하는 스크립트
"""
import json
import os
from services.database_service import DatabaseService

def migrate_users(db: DatabaseService):
    """사용자 데이터 마이그레이션"""
    print("📋 사용자 데이터 마이그레이션 중...")
    
    with open('data/users.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = data.get('users', [])
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for user in users:
            cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, email, password, name, role, student_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user['user_id'], user['email'], user['password'], 
                  user['name'], user['role'], user.get('student_id')))
    
    print(f"  ✅ {len(users)}명의 사용자 마이그레이션 완료")

def migrate_courses(db: DatabaseService):
    """강의 데이터 마이그레이션"""
    print("📋 강의 데이터 마이그레이션 중...")
    
    with open('data/courses.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    courses = data.get('courses', [])
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for course in courses:
            # 수강 학생 리스트를 문자열로 변환
            students_str = ','.join(course.get('enrolled_students', []))
            
            cursor.execute('''
                INSERT OR REPLACE INTO courses 
                (course_id, course_name, professor_id, professor_name, enrolled_students)
                VALUES (?, ?, ?, ?, ?)
            ''', (course['course_id'], course['course_name'], course['professor_id'],
                  course['professor_name'], students_str))
            
            # weeks 정보 마이그레이션
            weeks = course.get('weeks', {})
            for week_str, week_info in weeks.items():
                week_num = int(week_str)
                deadline = week_info.get('upload_deadline')
                status = week_info.get('evaluation_status', 'pending')
                
                cursor.execute('''
                    INSERT OR REPLACE INTO course_weeks 
                    (course_id, week, upload_deadline, evaluation_status)
                    VALUES (?, ?, ?, ?)
                ''', (course['course_id'], week_num, deadline, status))
    
    print(f"  ✅ {len(courses)}개의 강의 마이그레이션 완료")

def migrate_materials(db: DatabaseService):
    """자료 데이터 마이그레이션"""
    print("📋 자료 데이터 마이그레이션 중...")
    
    with open('data/materials.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    materials = data.get('materials', [])
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for material in materials:
            # file_path를 gcs_path로 변환
            # storage/professor/... -> storage/professor/...
            file_path = material.get('file_path', '')
            gcs_path = file_path.replace('\\', '/') if file_path else ''
            
            # type 결정
            mat_type = 'professor' if material.get('is_professor_material', False) else 'student'
            
            cursor.execute('''
                INSERT OR REPLACE INTO materials 
                (material_id, course_id, week, type, uploader_id, uploader_name, 
                 filename, gcs_path, page_count, upload_date, download_count, view_count,
                 evaluation_score, evaluation_completed)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (material['material_id'], material['course_id'], material['week'],
                  mat_type, material['uploader_id'], material['uploader_name'],
                  material.get('file_name', material.get('filename', '')), gcs_path, material.get('page_count', 0),
                  material.get('upload_date'), material.get('download_count', 0),
                  material.get('view_count', 0), material.get('evaluation_score'),
                  1 if material.get('evaluation_completed', False) else 0))
    
    print(f"  ✅ {len(materials)}개의 자료 마이그레이션 완료")

def migrate_custom_pdfs(db: DatabaseService):
    """나만의 PDF 데이터 마이그레이션"""
    print("📋 나만의 PDF 데이터 마이그레이션 중...")
    
    with open('data/custom_pdfs.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    custom_pdfs = data.get('custom_pdfs', [])
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for pdf in custom_pdfs:
            # file_path를 gcs_path로 변환
            file_path = pdf.get('file_path', '')
            gcs_path = file_path.replace('\\', '/') if file_path else ''
            
            # title 필드 (file_name이나 title)
            title = pdf.get('title', pdf.get('file_name', 'untitled.pdf'))
            
            cursor.execute('''
                INSERT OR REPLACE INTO custom_pdfs 
                (custom_pdf_id, student_id, course_id, week, title, gcs_path, page_count, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (pdf['custom_pdf_id'], pdf['student_id'], pdf['course_id'],
                  pdf['week'], title, gcs_path, pdf.get('page_count', 0),
                  pdf.get('created_at')))
            
            # 선택된 페이지 정보
            selected_pages = pdf.get('selected_pages', pdf.get('page_selections', []))
            for idx, page_info in enumerate(selected_pages):
                # material_id와 page_number 필드명이 다를 수 있음
                mat_id = page_info.get('material_id', page_info.get('source_material_id'))
                page_num = page_info.get('page_number', page_info.get('page_num', 1))
                
                if mat_id:
                    cursor.execute('''
                        INSERT OR REPLACE INTO custom_pdf_pages 
                        (custom_pdf_id, material_id, page_number, order_index)
                        VALUES (?, ?, ?, ?)
                    ''', (pdf['custom_pdf_id'], mat_id, page_num, idx))
    
    print(f"  ✅ {len(custom_pdfs)}개의 커스텀 PDF 마이그레이션 완료")

def migrate_notifications(db: DatabaseService):
    """알림 데이터 마이그레이션"""
    print("📋 알림 데이터 마이그레이션 중...")
    
    with open('data/notifications.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    notifications = data.get('notifications', [])
    
    with db.get_connection() as conn:
        cursor = conn.cursor()
        for notif in notifications:
            # type 필드가 없으면 'general'로 설정
            notif_type = notif.get('type', 'general')
            
            cursor.execute('''
                INSERT OR REPLACE INTO notifications 
                (notification_id, user_id, message, type, related_id, is_read, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (notif['notification_id'], notif['user_id'], notif['message'],
                  notif_type, notif.get('related_id'), 
                  1 if notif.get('is_read', False) else 0,
                  notif.get('created_at')))
    
    print(f"  ✅ {len(notifications)}개의 알림 마이그레이션 완료")

def main():
    """메인 함수"""
    print("=" * 70)
    print("JSON → SQLite 마이그레이션 시작")
    print("=" * 70)
    print()
    
    # DatabaseService 초기화 (테이블 자동 생성)
    db = DatabaseService('data/database.db')
    print("✅ SQLite 데이터베이스 초기화 완료")
    print()
    
    try:
        # 각 데이터 마이그레이션
        migrate_users(db)
        migrate_courses(db)
        migrate_materials(db)
        migrate_custom_pdfs(db)
        migrate_notifications(db)
        
        print()
        print("=" * 70)
        print("✅ 모든 데이터 마이그레이션 완료!")
        print("=" * 70)
        print()
        print(f"SQLite DB 파일: {os.path.abspath('data/database.db')}")
        print()
        print("다음 단계:")
        print("1. SQLite DB 확인: sqlite3 data\\database.db")
        print("2. storage 폴더를 GCS에 업로드: gsutil -m rsync -r storage\\ gs://note-sharing-files\\storage\\")
        print("3. update_routes.py 실행하여 코드 변경")
        print()
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
