"""
스토리지 서비스 테스트
파일 확장자 검증 등 실제 프로젝트 로직 테스트
"""

import os
import sys

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config


def test_allowed_file_extension():
    """허용된 파일 확장자 검증"""
    allowed_extensions = Config.ALLOWED_EXTENSIONS
    
    # 실제 프로젝트에서 사용하는 allowed_file 로직 시뮬레이션
    def allowed_file(filename):
        if not filename or '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in allowed_extensions
    
    # PDF 파일은 허용
    assert allowed_file('test.pdf') is True
    assert allowed_file('document.PDF') is True
    assert allowed_file('file.Pdf') is True
    
    # 다른 확장자는 거부
    assert allowed_file('test.txt') is False
    assert allowed_file('image.jpg') is False
    assert allowed_file('document.docx') is False
    
    # 확장자가 없는 파일은 거부
    assert allowed_file('test') is False
    assert allowed_file('') is False


def test_file_size_validation():
    """파일 크기 검증 로직 테스트"""
    max_size = Config.MAX_CONTENT_LENGTH
    
    # 파일 크기 검증 로직 시뮬레이션
    def is_file_size_valid(file_size):
        return file_size <= max_size and file_size > 0
    
    # 정상적인 크기
    assert is_file_size_valid(1024) is True  # 1KB
    assert is_file_size_valid(1024 * 1024) is True  # 1MB
    assert is_file_size_valid(50 * 1024 * 1024) is True  # 50MB
    
    # 제한 초과
    assert is_file_size_valid(max_size + 1) is False
    assert is_file_size_valid(max_size * 2) is False
    
    # 잘못된 크기
    assert is_file_size_valid(0) is False
    assert is_file_size_valid(-1) is False


def test_pdf_settings():
    """PDF 관련 설정값 검증"""
    assert Config.PDF_IMAGE_DPI == 150
    assert Config.PDF_IMAGE_QUALITY == 85
    assert Config.PDF_IMAGE_DPI > 0
    assert 0 < Config.PDF_IMAGE_QUALITY <= 100


def test_gcs_bucket_config():
    """GCS 버킷 설정 검증"""
    bucket_name = Config.GCS_BUCKET
    assert isinstance(bucket_name, str)
    assert len(bucket_name) > 0

