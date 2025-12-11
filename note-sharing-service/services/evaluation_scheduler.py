# -*- coding: utf-8 -*-
"""
필기 평가 스케줄러 (SQLite + GCS 버전)
"""
import schedule
import time
import threading
from datetime import datetime
import os
import tempfile
from services.database_service import DatabaseService
from services.gcs_storage_service import GCSStorageService
from services.pdf_service import PDFService
from services.gemini_service import GeminiService

class EvaluationScheduler:
    """필기 평가 스케줄러"""
    
    def __init__(self, gemini_api_key: str = None):
        self.db = DatabaseService()
        self.storage = GCSStorageService()
        self.pdf_service = PDFService()
        self.gemini_service = GeminiService(api_key=gemini_api_key)
        self.running = False
        self.thread = None
    
    def check_and_evaluate_deadlines(self):
        """마감일이 지난 주차의 필기를 일괄 평가"""
        print("\n" + "=" * 70)
        print("[평가 스케줄러] 마감일 체크 시작...")
        print("=" * 70)
        
        courses = self.db.get_all_courses()
        evaluated_count = 0
        
        for course in courses:
            course_id = course['course_id']
            
            # 1~16주차 확인
            for week in range(1, 17):
                deadline = self.db.get_week_deadline(course_id, week)
                
                if not deadline:
                    continue
                
                # 마감일 확인
                try:
                    deadline_dt = datetime.fromisoformat(deadline.replace('Z', ''))
                    if datetime.now() < deadline_dt:
                        continue  # 아직 마감 안됨
                except:
                    continue
                
                # evaluation_status 확인
                weeks_config = course.get('weeks', {})
                week_str = str(week)
                evaluation_status = 'pending'
                if week_str in weeks_config:
                    evaluation_status = weeks_config[week_str].get('evaluation_status', 'pending')
                
                if evaluation_status == 'completed':
                    continue  # 이미 평가 완료
                
                print(f"\n[평가 시작] {course['course_name']} - {week}주차")
                
                # 학생 필기 조회
                materials = self.db.get_materials_by_course_week(course_id, week)
                student_materials = [m for m in materials if m['type'] == 'student']
                
                if not student_materials:
                    print(f"  ⚠️  평가할 학생 필기가 없습니다.")
                    self._mark_evaluation_completed(course_id, week)
                    continue
                
                print(f"  📝 평가 대상: {len(student_materials)}개 필기")
                
                # 각 필기 평가
                for material in student_materials:
                    if material.get('evaluation_score') is not None:
                        print(f"  ⏭️  {material['uploader_name']}님의 필기는 이미 평가되었습니다.")
                        continue
                    
                    try:
                        print(f"  🔍 평가 중: {material['uploader_name']}님의 필기...")
                        
                        # 썸네일 경로 확인
                        thumbnail_prefix = f"storage/thumbnails/{material['material_id']}/"
                        thumbnail_files = self.storage.list_files(thumbnail_prefix)
                        
                        if not thumbnail_files:
                            # 썸네일 생성
                            print(f"    썸네일 생성 중...")
                            thumbnail_files = self.pdf_service.convert_pdf_to_images_from_gcs(
                                material['gcs_path'],
                                material['material_id'],
                                self.storage
                            )
                        
                        if not thumbnail_files:
                            print(f"    ❌ 썸네일을 생성할 수 없습니다.")
                            continue
                        
                        # Gemini로 평가 (GCS Signed URL 사용)
                        thumbnail_urls = []
                        for thumb_path in thumbnail_files:
                            url = self.storage.get_signed_url(thumb_path, expiration=3600)
                            if url:
                                thumbnail_urls.append(url)
                        
                        evaluation_result = self.gemini_service.evaluate_material(
                            material['material_id'],
                            thumbnail_urls
                        )
                        
                        # 점수 저장
                        score = evaluation_result['overall_score']
                        with self.db.get_connection() as conn:
                            cursor = conn.cursor()
                            cursor.execute('''
                                UPDATE materials
                                SET evaluation_score = ?, evaluation_completed = 1
                                WHERE material_id = ?
                            ''', (score, material['material_id']))
                        
                        # 알림 생성
                        self.db.add_notification({
                            'user_id': material['uploader_id'],
                            'type': 'evaluation',
                            'related_id': material['material_id'],
                            'message': f'필기 평가 완료! {week}주차 자료가 {score}점을 받았습니다.'
                        })
                        
                        print(f"    ✅ 평가 완료: {score:.2f}점")
                        evaluated_count += 1
                        
                    except Exception as e:
                        print(f"    ❌ 평가 실패: {str(e)}")
                
                # 평가 상태 완료 처리
                self._mark_evaluation_completed(course_id, week)
                print(f"  ✅ {week}주차 평가 완료")
        
        print(f"\n[평가 스케줄러] 완료 - 총 {evaluated_count}개 필기 평가\n")
    
    def _mark_evaluation_completed(self, course_id: str, week: int):
        """평가 상태를 완료로 변경"""
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO course_weeks (course_id, week, evaluation_status)
                VALUES (?, ?, 'completed')
            ''', (course_id, week))
    
    def evaluate_now(self, course_id: str = None, week: int = None):
        """즉시 평가 실행 (수동 트리거)"""
        if course_id and week:
            print(f"[수동 평가] {course_id} - {week}주차")
            
            # 학생 필기 조회
            materials = self.db.get_materials_by_course_week(course_id, week)
            student_materials = [m for m in materials if m['type'] == 'student']
            
            for material in student_materials:
                if material.get('evaluation_score') is not None:
                    continue
                
                try:
                    # 썸네일 확인 및 생성
                    thumbnail_prefix = f"storage/thumbnails/{material['material_id']}/"
                    thumbnail_files = self.storage.list_files(thumbnail_prefix)
                    
                    if not thumbnail_files:
                        thumbnail_files = self.pdf_service.convert_pdf_to_images_from_gcs(
                            material['gcs_path'],
                            material['material_id'],
                            self.storage
                        )
                    
                    # Gemini 평가
                    thumbnail_urls = []
                    for thumb_path in thumbnail_files:
                        url = self.storage.get_signed_url(thumb_path, expiration=3600)
                        if url:
                            thumbnail_urls.append(url)
                    
                    evaluation_result = self.gemini_service.evaluate_material(
                        material['material_id'],
                        thumbnail_urls
                    )
                    
                    # 점수 저장
                    score = evaluation_result['overall_score']
                    with self.db.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute('''
                            UPDATE materials
                            SET evaluation_score = ?, evaluation_completed = 1
                            WHERE material_id = ?
                        ''', (score, material['material_id']))
                    
                    print(f"  ✅ 평가 완료: {material['uploader_name']} - {score:.2f}점")
                    
                except Exception as e:
                    print(f"  ❌ 평가 실패: {str(e)}")
            
            self._mark_evaluation_completed(course_id, week)
        else:
            # 전체 평가
            self.check_and_evaluate_deadlines()
    
    def start(self, check_interval_minutes: int = 60):
        """
        스케줄러 시작
        
        Args:
            check_interval_minutes: 마감일 체크 간격 (분)
        """
        if self.running:
            print("[평가 스케줄러] 이미 실행 중입니다.")
            return
        
        self.running = True
        
        # 즉시 한 번 실행
        self.check_and_evaluate_deadlines()
        
        # 주기적으로 실행
        schedule.every(check_interval_minutes).minutes.do(self.check_and_evaluate_deadlines)
        
        def run_scheduler():
            while self.running:
                schedule.run_pending()
                time.sleep(60)
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        print(f"[평가 스케줄러] 시작됨 - {check_interval_minutes}분마다 체크")
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        print("[평가 스케줄러] 중지됨")
