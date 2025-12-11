# -*- coding: utf-8 -*-
"""
SQLite 기반 데이터 관리 서비스
"""
import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager

class DatabaseService:
    """SQLite 기반 데이터 관리"""
    
    def __init__(self, db_path='data/database.db'):
        self.db_path = db_path
        self._init_database()
    
    @contextmanager
    def get_connection(self):
        """DB 연결 컨텍스트 매니저"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 딕셔너리 형태로 결과 반환
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_database(self):
        """데이터베이스 초기화 (테이블 생성)"""
        # data 디렉토리 생성
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    name TEXT NOT NULL,
                    role TEXT NOT NULL,
                    student_id TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Courses 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS courses (
                    course_id TEXT PRIMARY KEY,
                    course_name TEXT NOT NULL,
                    professor_id TEXT NOT NULL,
                    professor_name TEXT NOT NULL,
                    enrolled_students TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (professor_id) REFERENCES users(user_id)
                )
            ''')
            
            # Course Weeks 테이블 (주차별 설정)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS course_weeks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    course_id TEXT NOT NULL,
                    week INTEGER NOT NULL,
                    upload_deadline TEXT,
                    evaluation_status TEXT DEFAULT 'pending',
                    FOREIGN KEY (course_id) REFERENCES courses(course_id),
                    UNIQUE(course_id, week)
                )
            ''')
            
            # Materials 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS materials (
                    material_id TEXT PRIMARY KEY,
                    course_id TEXT NOT NULL,
                    week INTEGER NOT NULL,
                    type TEXT NOT NULL,
                    uploader_id TEXT NOT NULL,
                    uploader_name TEXT NOT NULL,
                    filename TEXT NOT NULL,
                    gcs_path TEXT NOT NULL,
                    page_count INTEGER DEFAULT 0,
                    upload_date TEXT DEFAULT CURRENT_TIMESTAMP,
                    download_count INTEGER DEFAULT 0,
                    view_count INTEGER DEFAULT 0,
                    evaluation_score REAL,
                    evaluation_completed INTEGER DEFAULT 0,
                    FOREIGN KEY (course_id) REFERENCES courses(course_id),
                    FOREIGN KEY (uploader_id) REFERENCES users(user_id)
                )
            ''')
            
            # Custom PDFs 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_pdfs (
                    custom_pdf_id TEXT PRIMARY KEY,
                    student_id TEXT NOT NULL,
                    course_id TEXT NOT NULL,
                    week INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    gcs_path TEXT NOT NULL,
                    page_count INTEGER NOT NULL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (student_id) REFERENCES users(user_id),
                    FOREIGN KEY (course_id) REFERENCES courses(course_id)
                )
            ''')
            
            # Custom PDF Pages 테이블 (선택된 페이지 정보)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS custom_pdf_pages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    custom_pdf_id TEXT NOT NULL,
                    material_id TEXT NOT NULL,
                    page_number INTEGER NOT NULL,
                    order_index INTEGER NOT NULL,
                    FOREIGN KEY (custom_pdf_id) REFERENCES custom_pdfs(custom_pdf_id),
                    FOREIGN KEY (material_id) REFERENCES materials(material_id)
                )
            ''')
            
            # Notifications 테이블
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS notifications (
                    notification_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    message TEXT NOT NULL,
                    type TEXT NOT NULL,
                    related_id TEXT,
                    is_read INTEGER DEFAULT 0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # 인덱스 생성
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_materials_course_week ON materials(course_id, week)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_custom_pdfs_student ON custom_pdfs(student_id)')
    
    def _row_to_dict(self, row) -> Dict:
        """sqlite3.Row를 딕셔너리로 변환"""
        if row is None:
            return None
        return dict(row)
    
    # ===== 사용자 관련 =====
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """사용자 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
            return self._row_to_dict(cursor.fetchone())
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """로그인 인증"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users WHERE email = ? AND password = ?', (email, password))
            return self._row_to_dict(cursor.fetchone())
    
    def create_user(self, user: Dict) -> str:
        """새 사용자 생성"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # 이메일 중복 확인
            cursor.execute('SELECT user_id FROM users WHERE email = ?', (user['email'],))
            if cursor.fetchone():
                raise ValueError('이미 존재하는 이메일입니다.')
            
            # user_id 자동 생성
            if user['role'] == 'professor':
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'professor'")
                count = cursor.fetchone()['count']
                user_id = f"P{count + 1:05d}"
            else:  # student
                cursor.execute("SELECT COUNT(*) as count FROM users WHERE role = 'student'")
                count = cursor.fetchone()['count']
                user_id = f"{202300000 + count + 1}"
            
            cursor.execute('''
                INSERT INTO users (user_id, email, password, name, role, student_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (user_id, user['email'], user['password'], user['name'], 
                  user['role'], user.get('student_id', user_id if user['role'] == 'student' else None)))
            
            return user_id
    
    def get_all_users(self) -> List[Dict]:
        """모든 사용자 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM users')
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    # ===== 강의 관련 =====
    def get_all_courses(self) -> List[Dict]:
        """모든 강의 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM courses')
            courses = [self._row_to_dict(row) for row in cursor.fetchall()]
            # enrolled_students를 리스트로 변환
            for course in courses:
                if course['enrolled_students']:
                    course['enrolled_students'] = course['enrolled_students'].split(',')
                else:
                    course['enrolled_students'] = []
            return courses
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """강의 ID로 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM courses WHERE course_id = ?', (course_id,))
            course = self._row_to_dict(cursor.fetchone())
            if course and course['enrolled_students']:
                course['enrolled_students'] = course['enrolled_students'].split(',')
            elif course:
                course['enrolled_students'] = []
            
            # weeks 정보 추가
            if course:
                cursor.execute('''
                    SELECT week, upload_deadline, evaluation_status 
                    FROM course_weeks 
                    WHERE course_id = ?
                ''', (course_id,))
                weeks_data = cursor.fetchall()
                course['weeks'] = {}
                for row in weeks_data:
                    week_dict = dict(row)
                    course['weeks'][str(week_dict['week'])] = {
                        'upload_deadline': week_dict['upload_deadline'],
                        'evaluation_status': week_dict['evaluation_status']
                    }
            
            return course
    
    def get_courses_by_student(self, student_id: str) -> List[Dict]:
        """학생이 수강하는 강의 목록"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM courses 
                WHERE enrolled_students LIKE ?
            ''', (f'%{student_id}%',))
            courses = [self._row_to_dict(row) for row in cursor.fetchall()]
            for course in courses:
                if course['enrolled_students']:
                    course['enrolled_students'] = course['enrolled_students'].split(',')
                else:
                    course['enrolled_students'] = []
            return courses
    
    def get_courses_by_professor(self, professor_id: str) -> List[Dict]:
        """교수가 담당하는 강의 목록"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM courses WHERE professor_id = ?', (professor_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def add_course(self, course: Dict) -> str:
        """강의 추가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # course_id 자동 생성
            cursor.execute('SELECT COUNT(*) as count FROM courses')
            count = cursor.fetchone()['count']
            course_id = f"C{count + 1:03d}"
            
            # enrolled_students를 문자열로 변환
            students_str = ','.join(course.get('enrolled_students', []))
            
            cursor.execute('''
                INSERT INTO courses (course_id, course_name, professor_id, professor_name, enrolled_students)
                VALUES (?, ?, ?, ?, ?)
            ''', (course_id, course['course_name'], course['professor_id'], 
                  course['professor_name'], students_str))
            
            return course_id
    
    def set_week_deadline(self, course_id: str, week: int, deadline: str):
        """주차별 업로드 마감일 설정"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO course_weeks (course_id, week, upload_deadline, evaluation_status)
                VALUES (?, ?, ?, 'pending')
            ''', (course_id, week, deadline))
    
    def get_week_deadline(self, course_id: str, week: int) -> Optional[str]:
        """주차별 업로드 마감일 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT upload_deadline FROM course_weeks 
                WHERE course_id = ? AND week = ?
            ''', (course_id, week))
            row = cursor.fetchone()
            return row['upload_deadline'] if row else None
    
    def is_upload_period_open(self, course_id: str, week: int) -> bool:
        """업로드 기간이 열려있는지 확인"""
        deadline = self.get_week_deadline(course_id, week)
        if not deadline:
            return True
        
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', ''))
            return datetime.now() < deadline_dt
        except:
            return True
    
    def can_view_materials(self, course_id: str, week: int) -> bool:
        """자료 열람 가능 여부"""
        deadline = self.get_week_deadline(course_id, week)
        if not deadline:
            return True
        
        try:
            deadline_dt = datetime.fromisoformat(deadline.replace('Z', ''))
            return datetime.now() >= deadline_dt
        except:
            return True
    
    # ===== 자료 관련 =====
    def get_materials_by_course_week(self, course_id: str, week: int) -> List[Dict]:
        """특정 강의의 특정 주차 자료 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM materials 
                WHERE course_id = ? AND week = ?
                ORDER BY upload_date DESC
            ''', (course_id, week))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_materials_by_course(self, course_id: str) -> List[Dict]:
        """특정 강의의 모든 자료 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM materials 
                WHERE course_id = ?
                ORDER BY week, upload_date DESC
            ''', (course_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def add_material(self, material: Dict) -> str:
        """자료 추가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # material_id 자동 생성
            cursor.execute('SELECT COUNT(*) as count FROM materials')
            count = cursor.fetchone()['count']
            material_id = f"M{count + 1:03d}"
            
            cursor.execute('''
                INSERT INTO materials 
                (material_id, course_id, week, type, uploader_id, uploader_name, 
                 filename, gcs_path, page_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (material_id, material['course_id'], material['week'], 
                  material['type'], material['uploader_id'], material['uploader_name'],
                  material['filename'], material['gcs_path'], material.get('page_count', 0)))
            
            return material_id
    
    def get_material_by_id(self, material_id: str) -> Optional[Dict]:
        """자료 ID로 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM materials WHERE material_id = ?', (material_id,))
            return self._row_to_dict(cursor.fetchone())
    
    def increment_download_count(self, material_id: str):
        """다운로드 수 증가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE materials 
                SET download_count = download_count + 1 
                WHERE material_id = ?
            ''', (material_id,))
    
    def increment_view_count(self, material_id: str):
        """조회 수 증가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE materials 
                SET view_count = view_count + 1 
                WHERE material_id = ?
            ''', (material_id,))
    
    # ===== 나만의 PDF 관련 =====
    def add_custom_pdf(self, custom_pdf: Dict) -> str:
        """나만의 PDF 추가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # custom_pdf_id 자동 생성
            cursor.execute('SELECT COUNT(*) as count FROM custom_pdfs')
            count = cursor.fetchone()['count']
            custom_pdf_id = f"CP{count + 1:03d}"
            
            cursor.execute('''
                INSERT INTO custom_pdfs 
                (custom_pdf_id, student_id, course_id, week, title, gcs_path, page_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (custom_pdf_id, custom_pdf['student_id'], custom_pdf['course_id'],
                  custom_pdf['week'], custom_pdf['title'], custom_pdf['gcs_path'],
                  custom_pdf['page_count']))
            
            # 선택된 페이지 정보 저장
            if 'selected_pages' in custom_pdf:
                for idx, page_info in enumerate(custom_pdf['selected_pages']):
                    cursor.execute('''
                        INSERT INTO custom_pdf_pages 
                        (custom_pdf_id, material_id, page_number, order_index)
                        VALUES (?, ?, ?, ?)
                    ''', (custom_pdf_id, page_info['material_id'], 
                          page_info['page_number'], idx))
            
            return custom_pdf_id
    
    def get_custom_pdfs_by_student(self, student_id: str) -> List[Dict]:
        """학생의 나만의 PDF 목록"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM custom_pdfs 
                WHERE student_id = ?
                ORDER BY created_at DESC
            ''', (student_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def get_custom_pdf_by_id(self, custom_pdf_id: str) -> Optional[Dict]:
        """나만의 PDF 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM custom_pdfs WHERE custom_pdf_id = ?', (custom_pdf_id,))
            pdf = self._row_to_dict(cursor.fetchone())
            
            if pdf:
                # 선택된 페이지 정보 조회
                cursor.execute('''
                    SELECT * FROM custom_pdf_pages 
                    WHERE custom_pdf_id = ?
                    ORDER BY order_index
                ''', (custom_pdf_id,))
                pdf['selected_pages'] = [self._row_to_dict(row) for row in cursor.fetchall()]
            
            return pdf
    
    # ===== 알림 관련 =====
    def add_notification(self, notification: Dict):
        """알림 추가"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # notification_id 자동 생성
            cursor.execute('SELECT COUNT(*) as count FROM notifications')
            count = cursor.fetchone()['count']
            notification_id = f"N{count + 1:03d}"
            
            cursor.execute('''
                INSERT INTO notifications 
                (notification_id, user_id, message, type, related_id)
                VALUES (?, ?, ?, ?, ?)
            ''', (notification_id, notification['user_id'], notification['message'],
                  notification['type'], notification.get('related_id')))
    
    def get_notifications_by_user(self, user_id: str, unread_only=False) -> List[Dict]:
        """사용자 알림 조회"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if unread_only:
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE user_id = ? AND is_read = 0
                    ORDER BY created_at DESC
                ''', (user_id,))
            else:
                cursor.execute('''
                    SELECT * FROM notifications 
                    WHERE user_id = ?
                    ORDER BY created_at DESC
                ''', (user_id,))
            return [self._row_to_dict(row) for row in cursor.fetchall()]
    
    def mark_notification_as_read(self, notification_id: str):
        """알림 읽음 처리"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE notifications 
                SET is_read = 1 
                WHERE notification_id = ?
            ''', (notification_id,))
    
    def get_unread_notification_count(self, user_id: str) -> int:
        """읽지 않은 알림 개수"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT COUNT(*) as count FROM notifications 
                WHERE user_id = ? AND is_read = 0
            ''', (user_id,))
            return cursor.fetchone()['count']
