# -*- coding: utf-8 -*-
"""
애플리케이션 설정 파일 (SQLite + GCS 버전)
"""
import os

class Config:
    """기본 설정"""
    
    # 기본 경로
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')  # SQLite DB 저장 경로
    
    # GCS 설정
    GCS_BUCKET = os.getenv('GCS_BUCKET', 'note-sharing-files')
    
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # 세션 설정 (크로스 도메인 허용)
    SESSION_COOKIE_SAMESITE = 'None'  # 크로스 도메인 허용
    SESSION_COOKIE_SECURE = os.getenv('SESSION_SECURE', 'False') == 'True'  # HTTPS 사용 시 True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = None
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # PDF 이미지 변환 설정
    PDF_IMAGE_DPI = 150  # 해상도
    PDF_IMAGE_QUALITY = 85  # JPEG 품질
    
    @staticmethod
    def init_app(app):
        """애플리케이션 초기화"""
        # SQLite DB 디렉토리만 생성
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        
        # 초기 데이터 자동 생성
        Config.init_demo_data()
    
    @staticmethod
    def init_demo_data():
        """초기 데모 데이터 생성 (최초 1회만)"""
        # 플래그 파일로 초기화 여부 확인
        flag_file = os.path.join(Config.DATA_DIR, '.initialized')
        if os.path.exists(flag_file):
            print("✅ 초기 데이터가 이미 존재합니다. 스킵.")
            return
        
        from services.database_service import DatabaseService
        
        db = DatabaseService()
        
        # 테스트 사용자들
        test_users = [
            {'email': 'kim.prof@university.ac.kr', 'password': 'prof1234', 'name': '김교수', 'role': 'professor'},
            {'email': 'lee.prof@university.ac.kr', 'password': 'prof5678', 'name': '이교수', 'role': 'professor'},
            {'email': 'hong@student.ac.kr', 'password': 'student1', 'name': '홍길동', 'role': 'student'},
            {'email': 'kim@student.ac.kr', 'password': 'student2', 'name': '김철수', 'role': 'student'},
            {'email': 'lee@student.ac.kr', 'password': 'student3', 'name': '이영희', 'role': 'student'}
        ]
        
        # 사용자 생성 (이미 있으면 무시)
        for user_data in test_users:
            try:
                if not db.get_user_by_email(user_data['email']):
                    db.create_user(user_data)
                    print(f"✅ 사용자 생성: {user_data['email']}")
            except:
                pass
        
        # 심화프로젝트랩 강의 확인
        professor = db.get_user_by_email('kim.prof@university.ac.kr')
        if professor:
            with db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT course_id FROM courses WHERE course_name = '심화프로젝트랩'")
                existing = cursor.fetchone()
                
                if not existing:
                    # 강의 생성
                    course_data = {
                        'course_name': '심화프로젝트랩',
                        'professor_id': professor['user_id'],
                        'professor_name': professor['name'],
                        'enrolled_students': []
                    }
                    course_id = db.add_course(course_data)
                    
                    # 주차별 마감일 설정
                    deadline = "2024-12-16T23:59:59"
                    for week in range(1, 6):
                        db.set_week_deadline(course_id, week, deadline)
                    
                    # 초대 링크 생성
                    invitation_code = db.create_invitation(
                        course_id=course_id,
                        created_by=professor['user_id'],
                        expires_at=None,
                        max_uses=-1
                    )
                    
                    print(f"✅ 심화프로젝트랩 강의 생성 완료!")
                    print(f"   초대 코드: {invitation_code}")
        
        # 초기화 완료 플래그 생성
        with open(flag_file, 'w') as f:
            f.write('initialized')
        print("✅ 초기 데이터 생성 완료!")
