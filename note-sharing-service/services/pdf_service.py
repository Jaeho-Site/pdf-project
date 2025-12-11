# -*- coding: utf-8 -*-
"""
PDF 처리 서비스 (GCS 버전)
"""
from PyPDF2 import PdfReader, PdfWriter
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
from typing import List, Optional
from io import BytesIO

class PDFService:
    """PDF 처리 서비스 (GCS 연동)"""
    
    def __init__(self, poppler_path=None):
        self.poppler_path = poppler_path or self._find_poppler()
    
    def _find_poppler(self) -> Optional[str]:
        """Poppler 경로 자동 감지 (Windows)"""
        possible_paths = [
            r"C:\poppler-25.07.0\Library\bin",
            r"C:\poppler\Library\bin",
            r"C:\Program Files\poppler\bin",
            r"C:\poppler-0.68.0\bin",
            os.path.join(os.environ.get('LOCALAPPDATA', ''), 'poppler', 'bin'),
        ]
        
        for path in possible_paths:
            if os.path.exists(path) and os.path.exists(os.path.join(path, 'pdftoppm.exe')):
                print(f"  [Poppler] 자동 감지: {path}")
                return path
        
        return None
    
    def get_page_count(self, pdf_path: str) -> int:
        """PDF 페이지 수 조회"""
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception as e:
            print(f"PDF 페이지 수 조회 오류: {e}")
            return 0
    
    def convert_pdf_to_images_from_gcs(self, gcs_path: str, material_id: str, 
                                      storage, dpi=150) -> List[str]:
        """
        GCS의 PDF를 페이지별 이미지로 변환하여 GCS에 저장
        
        Args:
            gcs_path: PDF의 GCS 경로
            material_id: 자료 ID
            storage: GCSStorageService 인스턴스
            dpi: 이미지 해상도
            
        Returns:
            썸네일 GCS 경로 리스트
        """
        print(f"  [PDF→IMG] GCS에서 다운로드 중: {gcs_path}")
        
        # GCS에서 임시 다운로드
        temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix='.pdf')
        
        try:
            if not storage.download_file(gcs_path, temp_pdf.name):
                raise Exception("GCS 다운로드 실패")
            
            # PDF → 이미지 변환
            poppler_kwargs = {}
            if self.poppler_path:
                poppler_kwargs['poppler_path'] = self.poppler_path
            
            images = convert_from_path(temp_pdf.name, dpi=dpi, **poppler_kwargs)
            print(f"  [PDF→IMG] {len(images)}페이지 변환 완료")
            
            # 각 이미지를 GCS에 업로드
            thumbnail_paths = []
            for i, image in enumerate(images):
                # 이미지를 바이트로 변환
                img_buffer = BytesIO()
                image.save(img_buffer, 'JPEG', quality=85, optimize=True)
                img_bytes = img_buffer.getvalue()
                
                # GCS에 업로드
                gcs_thumb_path = storage.save_thumbnail(img_bytes, material_id, i + 1)
                if gcs_thumb_path:
                    thumbnail_paths.append(gcs_thumb_path)
                    print(f"  [GCS] 썸네일 업로드: page_{i+1}.jpg")
            
            return thumbnail_paths
            
        except Exception as e:
            print(f"  [ERROR] 썸네일 생성 실패: {e}")
            raise e
        finally:
            if os.path.exists(temp_pdf.name):
                os.unlink(temp_pdf.name)
