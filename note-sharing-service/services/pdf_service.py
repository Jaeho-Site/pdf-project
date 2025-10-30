# -*- coding: utf-8 -*-
"""
PDF 처리 서비스
"""
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from pdf2image import convert_from_path
from PIL import Image
import os
from typing import List, Dict, Optional

class PDFService:
    """PDF 처리 서비스"""
    
    def __init__(self, storage_dir='storage'):
        self.storage_dir = storage_dir
        self.thumbnail_dir = os.path.join(storage_dir, 'thumbnails')
        self.temp_dir = os.path.join(storage_dir, 'temp')
    
    def get_page_count(self, pdf_path: str) -> int:
        """PDF 페이지 수 조회"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"PDF 페이지 수 조회 오류: {e}")
            return 0
    
    def convert_pdf_to_images(self, pdf_path: str, material_id: str, 
                             dpi=150, force=False) -> List[str]:
        """
        PDF를 페이지별 이미지로 변환 (캐싱)
        
        Args:
            pdf_path: PDF 파일 경로
            material_id: 자료 ID (캐시 폴더명)
            dpi: 이미지 해상도
            force: 강제 재생성 여부
            
        Returns:
            이미지 파일 경로 리스트
        """
        thumbnail_folder = os.path.join(self.thumbnail_dir, material_id)
        
        # 이미 변환된 경우 캐시 사용
        if not force and os.path.exists(thumbnail_folder):
            images = sorted([
                os.path.join(thumbnail_folder, f) 
                for f in os.listdir(thumbnail_folder) 
                if f.endswith('.jpg')
            ])
            if images:
                return images
        
        # 폴더 생성
        os.makedirs(thumbnail_folder, exist_ok=True)
        
        try:
            # PDF → 이미지 변환
            images = convert_from_path(pdf_path, dpi=dpi)
            
            image_paths = []
            for i, image in enumerate(images, start=1):
                image_path = os.path.join(thumbnail_folder, f'page_{i}.jpg')
                image.save(image_path, 'JPEG', quality=85)
                image_paths.append(image_path)
            
            return image_paths
        
        except Exception as e:
            print(f"PDF → 이미지 변환 오류: {e}")
            return []
    
    def get_thumbnail_paths(self, material_id: str) -> List[str]:
        """썸네일 이미지 경로 조회 (이미 생성된 경우)"""
        thumbnail_folder = os.path.join(self.thumbnail_dir, material_id)
        
        if not os.path.exists(thumbnail_folder):
            return []
        
        images = sorted([
            os.path.join(thumbnail_folder, f) 
            for f in os.listdir(thumbnail_folder) 
            if f.endswith('.jpg')
        ])
        
        return images
    
    def create_custom_pdf(self, page_selections: List[Dict], 
                         output_path: str) -> bool:
        """
        선택된 페이지들로 새로운 PDF 생성
        
        Args:
            page_selections: 선택된 페이지 정보 리스트
                [
                    {
                        'source_material_id': 'M001',
                        'source_pdf_path': 'storage/.../file.pdf',
                        'page_num': 1  # 1-based
                    },
                    ...
                ]
            output_path: 출력 PDF 경로
            
        Returns:
            성공 여부
        """
        try:
            merger = PdfMerger()
            temp_files = []
            
            os.makedirs(self.temp_dir, exist_ok=True)
            
            for idx, selection in enumerate(page_selections):
                source_pdf = selection['source_pdf_path']
                page_num = selection['page_num'] - 1  # 0-based
                
                # 원본 PDF에서 해당 페이지 추출
                reader = PdfReader(source_pdf)
                
                # 페이지 번호 유효성 검사
                if page_num < 0 or page_num >= len(reader.pages):
                    print(f"경고: 페이지 번호 {page_num + 1}이 범위를 벗어남 (최대 {len(reader.pages)})")
                    continue
                
                writer = PdfWriter()
                writer.add_page(reader.pages[page_num])
                
                # 임시 파일 생성
                temp_file = f"temp_{idx}_{selection['source_material_id']}_page_{page_num + 1}.pdf"
                temp_path = os.path.join(self.temp_dir, temp_file)
                
                with open(temp_path, 'wb') as f:
                    writer.write(f)
                
                merger.append(temp_path)
                temp_files.append(temp_path)
            
            # 최종 PDF 생성
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            merger.write(output_path)
            merger.close()
            
            # 임시 파일 삭제
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    os.remove(temp_file)
            
            return True
            
        except Exception as e:
            print(f"PDF 생성 오류: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def get_pdf_info(self, pdf_path: str) -> Optional[Dict]:
        """PDF 정보 조회"""
        try:
            reader = PdfReader(pdf_path)
            return {
                'page_count': len(reader.pages),
                'file_size': os.path.getsize(pdf_path),
                'file_size_mb': round(os.path.getsize(pdf_path) / (1024 * 1024), 2)
            }
        except Exception as e:
            print(f"PDF 정보 조회 오류: {e}")
            return None
    
    def extract_page_as_pdf(self, source_pdf_path: str, page_num: int, 
                           output_path: str) -> bool:
        """단일 페이지를 별도 PDF로 추출"""
        try:
            reader = PdfReader(source_pdf_path)
            writer = PdfWriter()
            
            # 페이지 번호는 1-based
            writer.add_page(reader.pages[page_num - 1])
            
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            with open(output_path, 'wb') as f:
                writer.write(f)
            
            return True
            
        except Exception as e:
            print(f"페이지 추출 오류: {e}")
            return False

