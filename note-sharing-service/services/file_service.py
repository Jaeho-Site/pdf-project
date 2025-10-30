# -*- coding: utf-8 -*-
"""
파일 업로드/다운로드 서비스
"""
import os
import shutil
from werkzeug.utils import secure_filename
from typing import Optional, Tuple

class FileService:
    """파일 관리 서비스"""
    
    def __init__(self, storage_dir='storage'):
        self.storage_dir = storage_dir
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
            (파일 경로, 파일명) 또는 None
        """
        if not file or not self.allowed_file(file.filename):
            return None
        
        filename = secure_filename(file.filename)
        
        # 저장 경로: storage/professor/{course_id}/week_{week}/
        save_dir = os.path.join(
            self.storage_dir, 
            'professor', 
            course_id, 
            f'week_{week}'
        )
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        
        return (file_path, filename)
    
    def save_student_material(self, file, course_id: str, week: int, 
                             student_id: str) -> Optional[Tuple[str, str]]:
        """
        학생 필기 자료 저장
        
        Returns:
            (파일 경로, 파일명) 또는 None
        """
        if not file or not self.allowed_file(file.filename):
            return None
        
        filename = secure_filename(file.filename)
        
        # 저장 경로: storage/students/{student_id}/{course_id}/week_{week}/
        save_dir = os.path.join(
            self.storage_dir,
            'students',
            student_id,
            course_id,
            f'week_{week}'
        )
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, filename)
        file.save(file_path)
        
        return (file_path, filename)
    
    def save_custom_pdf(self, source_path: str, student_id: str, 
                       custom_pdf_id: str) -> Optional[str]:
        """
        나만의 PDF 저장
        
        Returns:
            파일 경로 또는 None
        """
        # 저장 경로: storage/custom/{student_id}/{custom_pdf_id}.pdf
        save_dir = os.path.join(
            self.storage_dir,
            'custom',
            student_id
        )
        os.makedirs(save_dir, exist_ok=True)
        
        file_path = os.path.join(save_dir, f'{custom_pdf_id}.pdf')
        
        try:
            shutil.copy2(source_path, file_path)
            return file_path
        except Exception as e:
            print(f"파일 복사 오류: {e}")
            return None
    
    def get_file_size(self, file_path: str) -> int:
        """파일 크기 조회 (바이트)"""
        if os.path.exists(file_path):
            return os.path.getsize(file_path)
        return 0
    
    def delete_file(self, file_path: str) -> bool:
        """파일 삭제"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            print(f"파일 삭제 오류: {e}")
            return False

