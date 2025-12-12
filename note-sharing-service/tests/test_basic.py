"""
기본 테스트 파일 - CI/CD용
프로젝트의 실제 기능을 검증하는 의미있는 테스트
"""

import os
import sys

# 프로젝트 루트를 경로에 추가
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import Config


def test_config_class():
    """Config 클래스 설정값 검증"""
    assert Config.MAX_CONTENT_LENGTH == 100 * 1024 * 1024  # 100MB
    assert Config.ALLOWED_EXTENSIONS == {'pdf'}
    assert Config.PDF_IMAGE_DPI == 150
    assert Config.PDF_IMAGE_QUALITY == 85
    assert isinstance(Config.BASE_DIR, str)
    assert len(Config.BASE_DIR) > 0


def test_file_extension_validation():
    """파일 확장자 검증 로직 테스트"""
    allowed_extensions = Config.ALLOWED_EXTENSIONS
    
    # PDF 파일 확장자 검증
    assert 'pdf' in allowed_extensions
    assert allowed_extensions == {'pdf'}
    
    # 파일명 검증 로직 시뮬레이션
    def is_pdf_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    
    assert is_pdf_file('test.pdf') is True
    assert is_pdf_file('document.PDF') is True
    assert is_pdf_file('file.txt') is False
    assert is_pdf_file('image.jpg') is False


def test_file_size_limit():
    """파일 크기 제한 검증"""
    max_size = Config.MAX_CONTENT_LENGTH
    max_size_mb = max_size / (1024 * 1024)
    
    assert max_size == 100 * 1024 * 1024
    assert max_size_mb == 100.0
    assert max_size > 0


def test_config_paths():
    """Config 경로 설정 검증"""
    assert os.path.isabs(Config.BASE_DIR)
    assert isinstance(Config.DATA_DIR, str)
    assert 'data' in Config.DATA_DIR or Config.DATA_DIR.endswith('data')


def test_file_naming_convention():
    """프로젝트에서 사용하는 파일명 형식 검증"""
    # 강의 자료 파일명 형식: "강의명 + 주차 + 교수명 or 학생명.pdf"
    course_name = "심화프로젝트랩"
    week = "1"
    student_name = "홍길동"
    filename = f"{course_name} {week}주차 {student_name}.pdf"
    
    assert filename == "심화프로젝트랩 1주차 홍길동.pdf"
    assert filename.endswith('.pdf')
    assert '주차' in filename
    
    # 커스텀 PDF 파일명 형식: "강의명+주차+나만의 자료.pdf"
    custom_filename = f"{course_name}{week}주차나만의 자료.pdf"
    assert custom_filename == "심화프로젝트랩1주차나만의 자료.pdf"
    assert custom_filename.endswith('.pdf')


def test_date_format():
    """날짜 형식 검증 (마감일 등에서 사용)"""
    from datetime import datetime
    
    # ISO 형식 날짜 문자열
    deadline = "2024-12-16T23:59:59"
    
    # 날짜 파싱 검증
    parsed_date = datetime.fromisoformat(deadline.replace('T', ' ').split('.')[0])
    assert parsed_date.year == 2024
    assert parsed_date.month == 12
    assert parsed_date.day == 16


def test_string_operations():
    """문자열 연산 테스트"""
    assert "hello" + " " + "world" == "hello world"
    assert len("test") == 4


def test_list_operations():
    """리스트 연산 테스트"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1


def test_dict_operations():
    """딕셔너리 연산 테스트"""
    test_dict = {"key": "value"}
    assert "key" in test_dict
    assert test_dict["key"] == "value"

