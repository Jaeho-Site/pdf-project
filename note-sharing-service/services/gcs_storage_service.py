# -*- coding: utf-8 -*-
"""
GCS(Google Cloud Storage) 파일 저장 서비스
"""
import os
from google.cloud import storage
from werkzeug.utils import secure_filename
from typing import Optional, Tuple
from io import BytesIO

class GCSStorageService:
    """GCS 기반 파일 관리 서비스"""
    
    def __init__(self, bucket_name=None):
        self.bucket_name = bucket_name or os.getenv('GCS_BUCKET', 'note-sharing-files')
        self.client = storage.Client()
        self.bucket = self.client.bucket(self.bucket_name)
        self.allowed_extensions = {'pdf'}
    
    def allowed_file(self, filename: str) -> bool:
        """허용된 파일 확장자인지 확인"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_professor_material(self, file, course_id: str, week: int, 
                                professor_id: str) -> Optional[Tuple[str, str]]:
        """
        교수 자료 저장
        
        Returns:
            (GCS 경로, 파일명) 또는 None
        """
        if not file or not self.allowed_file(file.filename):
            return None
        
        filename = secure_filename(file.filename)
        
        # GCS 경로: storage/professor/{course_id}/week_{week}/{filename}
        gcs_path = f"storage/professor/{course_id}/week_{week}/{filename}"
        
        # GCS에 업로드
        blob = self.bucket.blob(gcs_path)
        blob.upload_from_file(file, content_type='application/pdf')
        
        return (gcs_path, filename)
    
    def save_student_material(self, file, course_id: str, week: int, 
                             student_id: str) -> Optional[Tuple[str, str]]:
        """
        학생 필기 자료 저장
        
        Returns:
            (GCS 경로, 파일명) 또는 None
        """
        if not file or not self.allowed_file(file.filename):
            return None
        
        filename = secure_filename(file.filename)
        
        # GCS 경로: storage/students/{student_id}/{course_id}/week_{week}/{filename}
        gcs_path = f"storage/students/{student_id}/{course_id}/week_{week}/{filename}"
        
        # GCS에 업로드
        blob = self.bucket.blob(gcs_path)
        blob.upload_from_file(file, content_type='application/pdf')
        
        return (gcs_path, filename)
    
    def save_custom_pdf(self, pdf_bytes: bytes, student_id: str, 
                       custom_pdf_id: str) -> Optional[str]:
        """
        나만의 PDF 저장
        
        Args:
            pdf_bytes: PDF 파일 바이트 데이터
            student_id: 학생 ID
            custom_pdf_id: 커스텀 PDF ID
        
        Returns:
            GCS 경로 또는 None
        """
        # GCS 경로: storage/custom/{student_id}/{custom_pdf_id}.pdf
        gcs_path = f"storage/custom/{student_id}/{custom_pdf_id}.pdf"
        
        try:
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(pdf_bytes, content_type='application/pdf')
            return gcs_path
        except Exception as e:
            print(f"GCS 업로드 오류: {e}")
            return None
    
    def save_thumbnail(self, image_bytes: bytes, material_id: str, 
                      page_number: int) -> Optional[str]:
        """
        썸네일 이미지 저장
        
        Returns:
            GCS 경로 또는 None
        """
        # GCS 경로: storage/thumbnails/{material_id}/page_{page_number}.jpg
        gcs_path = f"storage/thumbnails/{material_id}/page_{page_number}.jpg"
        
        try:
            blob = self.bucket.blob(gcs_path)
            blob.upload_from_string(image_bytes, content_type='image/jpeg')
            return gcs_path
        except Exception as e:
            print(f"썸네일 업로드 오류: {e}")
            return None
    
    def download_file(self, gcs_path: str, destination_path: str) -> bool:
        """
        GCS에서 로컬로 파일 다운로드
        
        Args:
            gcs_path: GCS 경로
            destination_path: 로컬 저장 경로
        
        Returns:
            성공 여부
        """
        try:
            blob = self.bucket.blob(gcs_path)
            blob.download_to_filename(destination_path)
            return True
        except Exception as e:
            print(f"GCS 다운로드 오류: {e}")
            return False
    
    def download_to_memory(self, gcs_path: str) -> Optional[bytes]:
        """
        GCS에서 메모리로 파일 다운로드
        
        Returns:
            파일 바이트 데이터 또는 None
        """
        try:
            blob = self.bucket.blob(gcs_path)
            return blob.download_as_bytes()
        except Exception as e:
            print(f"GCS 다운로드 오류: {e}")
            return None
    
    def get_file_size(self, gcs_path: str) -> int:
        """파일 크기 조회 (바이트)"""
        try:
            blob = self.bucket.blob(gcs_path)
            blob.reload()
            return blob.size
        except:
            return 0
    
    def delete_file(self, gcs_path: str) -> bool:
        """파일 삭제"""
        try:
            blob = self.bucket.blob(gcs_path)
            blob.delete()
            return True
        except Exception as e:
            print(f"GCS 삭제 오류: {e}")
            return False
    
    def file_exists(self, gcs_path: str) -> bool:
        """파일 존재 여부 확인"""
        try:
            blob = self.bucket.blob(gcs_path)
            return blob.exists()
        except:
            return False
    
    def get_signed_url(self, gcs_path: str, expiration=3600) -> Optional[str]:
        """
        서명된 URL 생성 (다운로드용)
        
        Args:
            gcs_path: GCS 경로
            expiration: 유효 기간 (초)
        
        Returns:
            서명된 URL 또는 None
        """
        try:
            blob = self.bucket.blob(gcs_path)
            url = blob.generate_signed_url(
                version="v4",
                expiration=expiration,
                method="GET"
            )
            return url
        except Exception as e:
            print(f"서명된 URL 생성 오류: {e}")
            return None
    
    def list_files(self, prefix: str) -> list:
        """특정 경로의 파일 목록 조회"""
        try:
            blobs = self.bucket.list_blobs(prefix=prefix)
            return [blob.name for blob in blobs]
        except Exception as e:
            print(f"파일 목록 조회 오류: {e}")
            return []
