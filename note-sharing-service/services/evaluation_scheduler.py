# -*- coding: utf-8 -*-
"""
필기 평가 스케줄러 - 마감일 자동 감지 및 일괄 평가
"""
import schedule
import time
import threading
from datetime import datetime, timedelta
from typing import List, Dict
from services.data_service import DataService
from services.pdf_service import PDFService
from services.gemini_service import GeminiService
import os

def parse_datetime_safe(date_str: str) -> datetime:
    """ISO 형식 날짜 문자열을 datetime으로 변환 (Z 처리 포함)"""
    if not date_str:
        return None
    
    # Z를 +00:00로 변환 (UTC)
    if date_str.endswith('Z'):
        date_str = date_str[:-1] + '+00:00'
    
    try:
        return datetime.fromisoformat(date_str.replace('Z', ''))
    except ValueError:
        try:
            return datetime.fromisoformat(date_str)
        except ValueError:
            # dateutil parser 사용 (없으면 기본 파싱)
            try:
                from dateutil import parser
                return parser.parse(date_str)
            except:
                # 마지막 시도: 수동 파싱
                return datetime.strptime(date_str.replace('Z', ''), '%Y-%m-%dT%H:%M:%S.%f')

class EvaluationScheduler:
    """필기 평가 스케줄러"""
    
    def __init__(self, gemini_api_key: str = None):
        self.data_service = DataService()
        self.pdf_service = PDFService()
        self.gemini_service = GeminiService(api_key=gemini_api_key)
        self.running = False
        self.thread = None
    
    def check_and_evaluate_deadlines(self):
        """마감일이 지난 주차의 필기를 일괄 평가"""
        print("\n" + "=" * 70)
        print("[평가 스케줄러] 마감일 체크 시작...")
        print("=" * 70)
        
        courses = self.data_service.get_all_courses()
        evaluated_count = 0
        
        for course in courses:
            course_id = course['course_id']
            weeks_config = course.get('weeks', {})
            
            for week_str, week_info in weeks_config.items():
                week = int(week_str)
                deadline = week_info.get('upload_deadline')
                evaluation_status = week_info.get('evaluation_status', 'pending')
                
                if not deadline:
                    continue
                
                # 마감일 확인
                try:
                    deadline_dt = parse_datetime_safe(deadline)
                    if deadline_dt is None:
                        continue
                except Exception as e:
                    print(f"  ⚠️  마감일 파싱 오류: {deadline}, {e}")
                    continue
                
                now = datetime.now()
                
                # 마감일이 지났고 아직 평가되지 않은 경우
                if now > deadline_dt and evaluation_status != 'completed':
                    print(f"\n[평가 시작] {course['course_name']} - {week}주차")
                    print(f"  마감일: {deadline_dt.strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    # 해당 주차의 학생 필기 조회
                    materials = self.data_service.get_materials_by_course_week(course_id, week)
                    student_materials = [m for m in materials if not m['is_professor_material']]
                    
                    if not student_materials:
                        print(f"  ⚠️  평가할 학생 필기가 없습니다.")
                        # 평가 상태를 완료로 변경
                        self._update_evaluation_status(course_id, week, 'completed')
                        continue
                    
                    print(f"  📝 평가 대상: {len(student_materials)}개 필기")
                    
                    # 각 필기 평가
                    for material in student_materials:
                        if material.get('quality_score') is not None:
                            print(f"  ⏭️  {material['uploader_name']}님의 필기는 이미 평가되었습니다.")
                            continue
                        
                        try:
                            print(f"  🔍 평가 중: {material['uploader_name']}님의 필기...")
                            
                            # 썸네일 경로 가져오기
                            thumbnail_paths = self.pdf_service.get_thumbnail_paths(material['material_id'])
                            
                            if not thumbnail_paths:
                                # 썸네일이 없으면 생성
                                print(f"    썸네일 생성 중...")
                                thumbnail_paths = self.pdf_service.convert_pdf_to_images(
                                    material['file_path'],
                                    material['material_id']
                                )
                            
                            if not thumbnail_paths:
                                print(f"    ❌ 썸네일을 생성할 수 없습니다.")
                                continue
                            
                            # Gemini로 평가
                            evaluation_result = self.gemini_service.evaluate_material(
                                material['material_id'],
                                thumbnail_paths
                            )
                            
                            # 점수 저장
                            self._save_evaluation_result(material['material_id'], evaluation_result)
                            
                            print(f"    ✅ 평가 완료: {evaluation_result['overall_score']:.2f}점")
                            evaluated_count += 1
                            
                        except Exception as e:
                            print(f"    ❌ 평가 실패: {str(e)}")
                            import traceback
                            traceback.print_exc()
                    
                    # 평가 상태를 완료로 변경
                    self._update_evaluation_status(course_id, week, 'completed')
                    print(f"  ✅ {week}주차 평가 완료")
        
        print("\n" + "=" * 70)
        print(f"[평가 스케줄러] 완료 - 총 {evaluated_count}개 필기 평가")
        print("=" * 70 + "\n")
    
    def _save_evaluation_result(self, material_id: str, evaluation_result: Dict):
        """평가 결과를 materials.json에 저장"""
        data = self.data_service._load_json('materials')
        
        for material in data['materials']:
            if material['material_id'] == material_id:
                material['quality_score'] = evaluation_result['overall_score']
                material['readability_score'] = evaluation_result['readability']
                material['completeness_score'] = evaluation_result['completeness']
                material['organization_score'] = evaluation_result['organization']
                material['evaluation_date'] = datetime.now().isoformat()
                material['evaluation_feedback'] = evaluation_result['feedback']
                material['evaluation_strengths'] = evaluation_result.get('strengths', [])
                material['evaluation_improvements'] = evaluation_result.get('improvements', [])
                break
        
        self.data_service._save_json('materials', data)
    
    def _update_evaluation_status(self, course_id: str, week: int, status: str):
        """평가 상태 업데이트"""
        data = self.data_service._load_json('courses')
        
        for course in data['courses']:
            if course['course_id'] == course_id:
                if 'weeks' not in course:
                    course['weeks'] = {}
                
                week_str = str(week)
                if week_str not in course['weeks']:
                    course['weeks'][week_str] = {}
                
                course['weeks'][week_str]['evaluation_status'] = status
                break
        
        self.data_service._save_json('courses', data)
    
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
                time.sleep(60)  # 1분마다 체크
        
        self.thread = threading.Thread(target=run_scheduler, daemon=True)
        self.thread.start()
        
        print(f"[평가 스케줄러] 시작됨 (체크 간격: {check_interval_minutes}분)")
    
    def stop(self):
        """스케줄러 중지"""
        self.running = False
        schedule.clear()
        print("[평가 스케줄러] 중지됨")
    
    def evaluate_now(self, course_id: str = None, week: int = None):
        """
        즉시 평가 실행 (수동 트리거)
        
        Args:
            course_id: 특정 강의만 평가 (None이면 전체)
            week: 특정 주차만 평가 (None이면 전체)
        """
        if course_id and week:
            # 특정 강의/주차만 평가
            course = self.data_service.get_course_by_id(course_id)
            if not course:
                print(f"강의를 찾을 수 없습니다: {course_id}")
                return
            
            weeks_config = course.get('weeks', {})
            week_str = str(week)
            
            if week_str in weeks_config:
                week_info = weeks_config[week_str]
                deadline = week_info.get('upload_deadline')
                
                if deadline:
                    try:
                        deadline_dt = parse_datetime_safe(deadline)
                        if deadline_dt is None:
                            print(f"마감일을 파싱할 수 없습니다: {deadline}")
                            return
                    except Exception as e:
                        print(f"마감일 파싱 오류: {deadline}, {e}")
                        return
                    
                    if datetime.now() > deadline_dt:
                        # 마감일이 지났으면 평가
                        self._evaluate_week(course_id, week)
                    else:
                        print(f"마감일이 아직 지나지 않았습니다: {deadline_dt}")
                else:
                    print(f"마감일이 설정되지 않았습니다.")
            else:
                print(f"주차 정보를 찾을 수 없습니다: {week}주차")
        else:
            # 전체 평가
            self.check_and_evaluate_deadlines()
    
    def _evaluate_week(self, course_id: str, week: int):
        """특정 주차 평가 (내부 메서드)"""
        course = self.data_service.get_course_by_id(course_id)
        materials = self.data_service.get_materials_by_course_week(course_id, week)
        student_materials = [m for m in materials if not m['is_professor_material']]
        
        for material in student_materials:
            if material.get('quality_score') is not None:
                continue
            
            try:
                thumbnail_paths = self.pdf_service.get_thumbnail_paths(material['material_id'])
                if not thumbnail_paths:
                    thumbnail_paths = self.pdf_service.convert_pdf_to_images(
                        material['file_path'],
                        material['material_id']
                    )
                
                if thumbnail_paths:
                    evaluation_result = self.gemini_service.evaluate_material(
                        material['material_id'],
                        thumbnail_paths
                    )
                    self._save_evaluation_result(material['material_id'], evaluation_result)
            except Exception as e:
                print(f"평가 실패 ({material['uploader_name']}): {e}")

