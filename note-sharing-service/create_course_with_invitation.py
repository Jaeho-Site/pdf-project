# -*- coding: utf-8 -*-
"""
'심화프로젝트랩' 강의 생성 및 초대 링크 생성 스크립트
"""
from services.database_service import DatabaseService
from datetime import datetime

def create_advanced_project_course():
    """심화프로젝트랩 강의 생성"""
    db = DatabaseService()
    
    print("=" * 70)
    print("📚 '심화프로젝트랩' 강의 생성 중...")
    print("=" * 70)
    
    # 1. 교수 계정 확인 (kim.prof 사용)
    professor_email = 'kim.prof@university.ac.kr'
    professor = db.get_user_by_email(professor_email)
    
    if not professor:
        print(f"❌ 교수 계정을 찾을 수 없습니다: {professor_email}")
        return
    
    print(f"\n✅ 교수: {professor['name']} ({professor['email']})")
    
    # 2. 강의 생성
    course_data = {
        'course_name': '심화프로젝트랩',
        'professor_id': professor['user_id'],
        'professor_name': professor['name'],
        'enrolled_students': []
    }
    
    course_id = db.add_course(course_data)
    print(f"✅ 강의 생성 완료: {course_id}")
    
    # 3. 주차별 마감일 설정 (1~5주차, 12월 16일까지)
    deadline = "2024-12-16T23:59:59"
    for week in range(1, 6):
        db.set_week_deadline(course_id, week, deadline)
        print(f"  - {week}주차 마감일 설정: 2024-12-16 23:59:59")
    
    # 4. 초대 링크 생성
    invitation_code = db.create_invitation(
        course_id=course_id,
        created_by=professor['user_id'],
        expires_at=None,  # 만료 없음
        max_uses=-1  # 무제한 사용
    )
    
    print(f"\n🔗 초대 링크 생성 완료!")
    print(f"   코드: {invitation_code}")
    print(f"   URL: https://pdf-project-seven.vercel.app/invite/{invitation_code}")
    
    print("\n" + "=" * 70)
    print("✅ 모든 작업 완료!")
    print("=" * 70)
    print(f"\n📋 강의 정보:")
    print(f"   - 강의명: 심화프로젝트랩")
    print(f"   - 강의 ID: {course_id}")
    print(f"   - 교수: {professor['name']}")
    print(f"   - 주차: 1~5주")
    print(f"   - 업로드 마감: 2024년 12월 16일 23:59")
    print(f"   - 초대 코드: {invitation_code}")
    print(f"\n🔗 학생들에게 공유할 링크:")
    print(f"   https://pdf-project-seven.vercel.app/invite/{invitation_code}")
    print()

if __name__ == '__main__':
    create_advanced_project_course()

