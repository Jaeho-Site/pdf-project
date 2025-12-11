# -*- coding: utf-8 -*-
"""
애플리케이션 설정 파일 (SQLite + GCS 버전)
"""
import os

class Config:
    """기본 설정"""
    
    # 기본 경로
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')  # SQLite DB 저장 경로
    
    # GCS 설정
    GCS_BUCKET = os.getenv('GCS_BUCKET', 'note-sharing-files')
    
    # Flask 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True') == 'True'
    
    # 세션 설정
    SESSION_COOKIE_SAMESITE = 'Lax'
    SESSION_COOKIE_SECURE = False  # HTTP에서는 False, HTTPS에서는 True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_DOMAIN = None
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # PDF 이미지 변환 설정
    PDF_IMAGE_DPI = 150  # 해상도
    PDF_IMAGE_QUALITY = 85  # JPEG 품질
    
    @staticmethod
    def init_app(app):
        """애플리케이션 초기화"""
        # SQLite DB 디렉토리만 생성
        os.makedirs(Config.DATA_DIR, exist_ok=True)
