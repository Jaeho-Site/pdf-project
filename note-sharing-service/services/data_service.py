# -*- coding: utf-8 -*-
"""
JSON 파일 기반 데이터 관리 서비스
"""
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class DataService:
    """JSON 파일 기반 데이터 관리"""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.files = {
            'users': os.path.join(data_dir, 'users.json'),
            'courses': os.path.join(data_dir, 'courses.json'),
            'materials': os.path.join(data_dir, 'materials.json'),
            'custom_pdfs': os.path.join(data_dir, 'custom_pdfs.json'),
            'notifications': os.path.join(data_dir, 'notifications.json')
        }
    
    def _load_json(self, file_key: str) -> Dict:
        """JSON 파일 로드"""
        file_path = self.files[file_key]
        if not os.path.exists(file_path):
            return {file_key: []}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def _save_json(self, file_key: str, data: Dict):
        """JSON 파일 저장"""
        file_path = self.files[file_key]
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    # ===== 사용자 관련 =====
    def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        """사용자 조회"""
        data = self._load_json('users')
        for user in data['users']:
            if user['user_id'] == user_id:
                return user
        return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict]:
        """이메일로 사용자 조회"""
        data = self._load_json('users')
        for user in data['users']:
            if user['email'] == email:
                return user
        return None
    
    def authenticate_user(self, email: str, password: str) -> Optional[Dict]:
        """로그인 인증"""
        user = self.get_user_by_email(email)
        if user and user['password'] == password:
            return user
        return None
    
    def get_all_users(self) -> List[Dict]:
        """모든 사용자 조회"""
        data = self._load_json('users')
        return data.get('users', [])
    
    # ===== 강의 관련 =====
    def get_all_courses(self) -> List[Dict]:
        """모든 강의 조회"""
        data = self._load_json('courses')
        return data.get('courses', [])
    
    def get_course_by_id(self, course_id: str) -> Optional[Dict]:
        """강의 ID로 조회"""
        data = self._load_json('courses')
        for course in data['courses']:
            if course['course_id'] == course_id:
                return course
        return None
    
    def get_courses_by_student(self, student_id: str) -> List[Dict]:
        """학생이 수강하는 강의 목록"""
        data = self._load_json('courses')
        return [c for c in data['courses'] if student_id in c['enrolled_students']]
    
    def get_courses_by_professor(self, professor_id: str) -> List[Dict]:
        """교수가 담당하는 강의 목록"""
        data = self._load_json('courses')
        return [c for c in data['courses'] if c['professor_id'] == professor_id]
    
    def add_course(self, course: Dict) -> str:
        """강의 추가 (교수만)"""
        data = self._load_json('courses')
        
        # course_id 자동 생성
        course_count = len(data['courses'])
        course['course_id'] = f"C{course_count + 1:03d}"
        course['created_at'] = datetime.now().isoformat()
        
        data['courses'].append(course)
        self._save_json('courses', data)
        
        return course['course_id']
    
    # ===== 자료 관련 =====
    def get_materials_by_course_week(self, course_id: str, week: int) -> List[Dict]:
        """특정 강의의 특정 주차 자료 조회"""
        data = self._load_json('materials')
        return [m for m in data['materials'] 
                if m['course_id'] == course_id and m['week'] == week]
    
    def get_materials_by_course(self, course_id: str) -> List[Dict]:
        """특정 강의의 모든 자료 조회"""
        data = self._load_json('materials')
        return [m for m in data['materials'] if m['course_id'] == course_id]
    
    def add_material(self, material: Dict) -> str:
        """자료 추가"""
        data = self._load_json('materials')
        
        # material_id 자동 생성
        material_count = len(data['materials'])
        material['material_id'] = f"M{material_count + 1:03d}"
        material['upload_date'] = datetime.now().isoformat()
        material['download_count'] = 0
        material['view_count'] = 0
        
        data['materials'].append(material)
        self._save_json('materials', data)
        
        return material['material_id']
    
    def get_material_by_id(self, material_id: str) -> Optional[Dict]:
        """자료 ID로 조회"""
        data = self._load_json('materials')
        for material in data['materials']:
            if material['material_id'] == material_id:
                return material
        return None
    
    def increment_download_count(self, material_id: str):
        """다운로드 수 증가"""
        data = self._load_json('materials')
        for material in data['materials']:
            if material['material_id'] == material_id:
                material['download_count'] += 1
                break
        self._save_json('materials', data)
    
    def increment_view_count(self, material_id: str):
        """조회 수 증가"""
        data = self._load_json('materials')
        for material in data['materials']:
            if material['material_id'] == material_id:
                material['view_count'] += 1
                break
        self._save_json('materials', data)
    
    # ===== 나만의 PDF 관련 =====
    def add_custom_pdf(self, custom_pdf: Dict) -> str:
        """나만의 PDF 추가"""
        data = self._load_json('custom_pdfs')
        
        custom_pdf_count = len(data['custom_pdfs'])
        custom_pdf['custom_pdf_id'] = f"CP{custom_pdf_count + 1:03d}"
        custom_pdf['created_at'] = datetime.now().isoformat()
        
        data['custom_pdfs'].append(custom_pdf)
        self._save_json('custom_pdfs', data)
        
        return custom_pdf['custom_pdf_id']
    
    def get_custom_pdfs_by_student(self, student_id: str) -> List[Dict]:
        """학생의 나만의 PDF 목록"""
        data = self._load_json('custom_pdfs')
        return [cp for cp in data['custom_pdfs'] if cp['student_id'] == student_id]
    
    def get_custom_pdf_by_id(self, custom_pdf_id: str) -> Optional[Dict]:
        """나만의 PDF 조회"""
        data = self._load_json('custom_pdfs')
        for cp in data['custom_pdfs']:
            if cp['custom_pdf_id'] == custom_pdf_id:
                return cp
        return None
    
    # ===== 알림 관련 =====
    def add_notification(self, notification: Dict):
        """알림 추가"""
        data = self._load_json('notifications')
        
        notification_count = len(data['notifications'])
        notification['notification_id'] = f"N{notification_count + 1:03d}"
        notification['created_at'] = datetime.now().isoformat()
        notification['is_read'] = False
        
        data['notifications'].append(notification)
        self._save_json('notifications', data)
    
    def get_notifications_by_user(self, user_id: str, unread_only=False) -> List[Dict]:
        """사용자 알림 조회"""
        data = self._load_json('notifications')
        notifications = [n for n in data['notifications'] if n['user_id'] == user_id]
        
        if unread_only:
            notifications = [n for n in notifications if not n['is_read']]
        
        return sorted(notifications, key=lambda x: x['created_at'], reverse=True)
    
    def mark_notification_as_read(self, notification_id: str):
        """알림 읽음 처리"""
        data = self._load_json('notifications')
        for notification in data['notifications']:
            if notification['notification_id'] == notification_id:
                notification['is_read'] = True
                break
        self._save_json('notifications', data)
    
    def get_unread_notification_count(self, user_id: str) -> int:
        """읽지 않은 알림 개수"""
        notifications = self.get_notifications_by_user(user_id, unread_only=True)
        return len(notifications)

