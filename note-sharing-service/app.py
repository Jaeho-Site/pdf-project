# -*- coding: utf-8 -*-
"""
필기자료 공유 서비스 - API 서버 (React 전용)
SQLite + GCS 버전
"""
from flask import Flask
from flask_cors import CORS
from config import Config
from services.evaluation_scheduler import EvaluationScheduler
import os

def create_app():
    """Flask API 앱 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS 설정 (React 앱 연동) - 모든 origin 허용
    CORS(app, 
         supports_credentials=True, 
         origins='*',  # 모든 origin 허용
         allow_headers=['Content-Type', 'Authorization', 'X-User-ID', 'X-User-Role', 'X-User-Email', 'Accept', 'Content-Length'],
         expose_headers=['Content-Disposition', 'Content-Type', 'Content-Length'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS', 'PATCH'],
         max_age=3600)
    
    # CORS 헤더를 명시적으로 추가 (추가 보장)
    @app.after_request
    def after_request(response):
        origin = request.headers.get('Origin')
        if origin:
            response.headers.add('Access-Control-Allow-Origin', origin)
        else:
            response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-User-ID, X-User-Role, X-User-Email, Accept, Content-Length')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS, PATCH')
        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Max-Age', '3600')
        return response
    
    # 설정 초기화
    Config.init_app(app)
    
    # API 블루프린트 등록
    from routes.api_auth import api_auth_bp
    from routes.api_course import api_course_bp
    from routes.api_material import api_material_bp
    from routes.api_custom_pdf import api_custom_pdf_bp
    from routes.api_notification import api_notification_bp
    from routes.api_evaluation import api_evaluation_bp
    from routes.api_admin import api_admin_bp
    
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_course_bp, url_prefix='/api/courses')
    app.register_blueprint(api_material_bp, url_prefix='/api')
    app.register_blueprint(api_custom_pdf_bp, url_prefix='/api')
    app.register_blueprint(api_notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(api_evaluation_bp, url_prefix='/api')
    app.register_blueprint(api_admin_bp, url_prefix='/api/admin')
    
    # 헬스 체크
    @app.route('/api/health')
    def health_check():
        """API 서버 상태 확인"""
        return {
            'status': 'ok', 
            'message': 'API server is running',
            'storage': 'GCS',
            'database': 'SQLite'
        }, 200
    
    # 평가 스케줄러 초기화 (Gemini API 키가 있는 경우만)
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            app.config['EVALUATION_SCHEDULER'] = EvaluationScheduler(gemini_api_key=gemini_api_key)
            app.config['EVALUATION_SCHEDULER'].start(check_interval_minutes=60)
            print("✅ 평가 스케줄러가 시작되었습니다.")
        except Exception as e:
            print(f"⚠️  평가 스케줄러 시작 실패: {e}")
            app.config['EVALUATION_SCHEDULER'] = None
    else:
        print("⚠️  GEMINI_API_KEY가 설정되지 않아 평가 스케줄러를 시작하지 않습니다.")
        app.config['EVALUATION_SCHEDULER'] = None
    
    # 404 에러 핸들러
    @app.errorhandler(404)
    def not_found(e):
        return {'success': False, 'message': 'API endpoint not found'}, 404
    
    # 413 에러 핸들러 (파일 크기 초과)
    @app.errorhandler(413)
    def request_entity_too_large(e):
        max_size_mb = app.config.get("MAX_CONTENT_LENGTH", 0) // (1024*1024)
        max_size_kb = app.config.get("MAX_CONTENT_LENGTH", 0) // 1024
        return {'success': False, 'message': f'파일 크기가 너무 큽니다. 최대 {max_size_mb}MB ({max_size_kb}KB)까지 업로드 가능합니다.'}, 413
    
    # 500 에러 핸들러
    @app.errorhandler(500)
    def server_error(e):
        return {'success': False, 'message': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 70)
    print("🚀 필기자료 공유 서비스 - API 서버 (SQLite + GCS)")
    print("=" * 70)
    print("\n💾 데이터베이스: SQLite (data/database.db)")
    print("☁️  파일 저장소: Google Cloud Storage")
    print("\n📚 테스트 계정:")
    print("\n[교수 계정]")
    print("  - 김교수: kim.prof@university.ac.kr / prof1234")
    print("  - 이교수: lee.prof@university.ac.kr / prof5678")
    print("\n[학생 계정]")
    print("  - 홍길동: hong@student.ac.kr / student1")
    print("  - 김철수: kim@student.ac.kr / student2")
    print("  - 이영희: lee@student.ac.kr / student3")
    print("\n" + "=" * 70)
    print("🌐 API Server: http://localhost:5000/api")
    print("🌐 React Client: http://localhost:3000")
    print("=" * 70)
    print("\n📡 주요 API 엔드포인트:")
    print("  - POST   /api/auth/login")
    print("  - GET    /api/courses")
    print("  - POST   /api/courses/{id}/week/{week}/upload")
    print("  - GET    /api/materials/{id}/thumbnails")
    print("  - POST   /api/courses/{id}/week/{week}/generate-custom")
    print("\n✅ 서버 준비 완료!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
