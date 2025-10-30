# -*- coding: utf-8 -*-
"""
애플리케이션 설정 파일
"""
import os

class Config:
    """기본 설정"""
    
    # 기본 경로
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    STORAGE_DIR = os.path.join(BASE_DIR, 'storage')
    
    # Flask 설정
    SECRET_KEY = 'dev-secret-key-change-in-production'
    DEBUG = True
    
    # 세션 설정 (CORS를 위해)
    SESSION_COOKIE_SAMESITE = 'None'
    SESSION_COOKIE_SECURE = False  # 개발 환경에서는 False, 프로덕션에서는 True
    SESSION_COOKIE_HTTPONLY = True
    
    # 파일 업로드 설정
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS = {'pdf'}
    
    # PDF 이미지 변환 설정
    PDF_IMAGE_DPI = 150  # 해상도
    PDF_IMAGE_QUALITY = 85  # JPEG 품질
    
    @staticmethod
    def init_app(app):
        """애플리케이션 초기화"""
        # 필요한 디렉토리 생성
        os.makedirs(Config.DATA_DIR, exist_ok=True)
        os.makedirs(Config.STORAGE_DIR, exist_ok=True)
        os.makedirs(os.path.join(Config.STORAGE_DIR, 'professor'), exist_ok=True)
        os.makedirs(os.path.join(Config.STORAGE_DIR, 'students'), exist_ok=True)
        os.makedirs(os.path.join(Config.STORAGE_DIR, 'custom'), exist_ok=True)
        os.makedirs(os.path.join(Config.STORAGE_DIR, 'thumbnails'), exist_ok=True)
        os.makedirs(os.path.join(Config.STORAGE_DIR, 'temp'), exist_ok=True)
