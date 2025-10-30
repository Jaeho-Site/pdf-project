# -*- coding: utf-8 -*-
"""
기존 자료의 썸네일 일괄 생성 스크립트
"""
from services.data_service import DataService
from services.pdf_service import PDFService
import os

def generate_all_thumbnails():
    """모든 자료의 썸네일 생성"""
    data_service = DataService()
    pdf_service = PDFService()
    
    # materials.json 로드
    data = data_service._load_json('materials')
    materials = data.get('materials', [])
    
    print("=" * 70)
    print("📸 썸네일 일괄 생성 시작")
    print("=" * 70)
    print(f"총 {len(materials)}개의 자료 발견\n")
    
    success_count = 0
    fail_count = 0
    
    for material in materials:
        material_id = material['material_id']
        file_path = material['file_path']
        file_name = material['file_name']
        
        print(f"[{material_id}] {file_name}")
        
        # 파일 존재 여부 확인
        if not os.path.exists(file_path):
            print(f"  ❌ 파일 없음: {file_path}")
            fail_count += 1
            continue
        
        # 썸네일이 이미 있는지 확인
        thumbnail_paths = pdf_service.get_thumbnail_paths(material_id)
        if thumbnail_paths:
            print(f"  ✅ 이미 존재 ({len(thumbnail_paths)}개)")
            success_count += 1
            continue
        
        # 썸네일 생성
        try:
            print(f"  🖼️  생성 중...")
            thumbnail_paths = pdf_service.convert_pdf_to_images(file_path, material_id)
            print(f"  ✅ 생성 완료 ({len(thumbnail_paths)}개)")
            success_count += 1
        except Exception as e:
            print(f"  ❌ 실패: {e}")
            fail_count += 1
        
        print()
    
    print("=" * 70)
    print(f"✅ 성공: {success_count}개")
    print(f"❌ 실패: {fail_count}개")
    print("=" * 70)

if __name__ == '__main__':
    generate_all_thumbnails()

