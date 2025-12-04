# -*- coding: utf-8 -*-
"""
필기자료 공유 서비스 - API 서버 (React 전용)
"""
from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from services.evaluation_scheduler import EvaluationScheduler
import os

def create_app():
    """Flask API 앱 생성"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CORS 설정 (React 앱 연동)
    CORS(app, 
         supports_credentials=True, 
         origins=['http://localhost:3000'],
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # 설정 초기화
    Config.init_app(app)
    
    # API 블루프린트만 등록 (React용)
    from routes.api_auth import api_auth_bp
    from routes.api_course import api_course_bp
    from routes.api_material import api_material_bp
    from routes.api_custom_pdf import api_custom_pdf_bp
    from routes.api_notification import api_notification_bp
    from routes.api_evaluation import api_evaluation_bp
    
    app.register_blueprint(api_auth_bp, url_prefix='/api/auth')
    app.register_blueprint(api_course_bp, url_prefix='/api/courses')
    app.register_blueprint(api_material_bp, url_prefix='/api')  # /api/courses와 /api/materials 통합
    app.register_blueprint(api_custom_pdf_bp, url_prefix='/api')
    app.register_blueprint(api_notification_bp, url_prefix='/api/notifications')
    app.register_blueprint(api_evaluation_bp, url_prefix='/api')
    
    # 정적 파일 서빙 (썸네일 이미지)
    @app.route('/api/storage/<path:filename>')
    def serve_storage(filename):
        """스토리지 파일 서빙"""
        storage_path = os.path.join(app.root_path, 'storage')
        return send_from_directory(storage_path, filename)
    
    # 헬스 체크
    @app.route('/api/health')
    def health_check():
        """API 서버 상태 확인"""
        return {'status': 'ok', 'message': 'API server is running'}, 200
    
    # 평가 스케줄러 초기화 (Gemini API 키가 있는 경우만)
    # 주의: 스케줄러는 앱 컨텍스트 외부에서도 작동하도록 전역 변수로 저장
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if gemini_api_key:
        try:
            app.config['EVALUATION_SCHEDULER'] = EvaluationScheduler(gemini_api_key=gemini_api_key)
            app.config['EVALUATION_SCHEDULER'].start(check_interval_minutes=60)  # 1시간마다 체크
            print("✅ 평가 스케줄러가 시작되었습니다.")
        except Exception as e:
            print(f"⚠️  평가 스케줄러 시작 실패: {e}")
            print("   GEMINI_API_KEY 환경변수를 확인하세요.")
            app.config['EVALUATION_SCHEDULER'] = None
    else:
        print("⚠️  GEMINI_API_KEY가 설정되지 않아 평가 스케줄러를 시작하지 않습니다.")
        print("   필기 평가 기능을 사용하려면 .env 파일에 GEMINI_API_KEY를 설정하세요.")
        app.config['EVALUATION_SCHEDULER'] = None
    
    # 404 에러 핸들러
    @app.errorhandler(404)
    def not_found(e):
        return {'success': False, 'message': 'API endpoint not found'}, 404
    
    # 500 에러 핸들러
    @app.errorhandler(500)
    def server_error(e):
        return {'success': False, 'message': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 70)
    print("🚀 필기자료 공유 서비스 - API 서버 (React 전용)")
    print("=" * 70)
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
    print("  - GET    /api/courses/{id}/week/{week}/create-custom")
    print("  - POST   /api/custom-pdfs/generate")
    print("  - GET    /api/notifications")
    print("\n✅ 서버 준비 완료!\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
