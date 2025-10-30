# -*- coding: utf-8 -*-
"""
필기자료 공유 서비스 - 메인 애플리케이션
"""
from flask import Flask
from config import Config

def create_app():
    """Flask 앱 생성 및 설정"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 설정 초기화
    Config.init_app(app)
    
    # 블루프린트 등록
    from routes.auth import auth_bp
    from routes.main import main_bp
    from routes.course import course_bp
    from routes.material import material_bp
    from routes.custom_pdf import custom_pdf_bp
    
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(main_bp)
    app.register_blueprint(course_bp)
    app.register_blueprint(material_bp)
    app.register_blueprint(custom_pdf_bp)
    
    # 템플릿 필터 등록
    from utils.helpers import format_datetime, format_date, format_filesize
    app.jinja_env.filters['datetime'] = format_datetime
    app.jinja_env.filters['date'] = format_date
    app.jinja_env.filters['filesize'] = format_filesize
    
    return app

if __name__ == '__main__':
    app = create_app()
    print("=" * 60)
    print("필기자료 공유 서비스 시작!")
    print("=" * 60)
    print("\n📚 테스트 계정:")
    print("\n[교수 계정]")
    print("  - 김교수: kim.prof@university.ac.kr / prof1234")
    print("  - 이교수: lee.prof@university.ac.kr / prof5678")
    print("\n[학생 계정]")
    print("  - 홍길동: hong@student.ac.kr / student1")
    print("  - 김철수: kim@student.ac.kr / student2")
    print("  - 이영희: lee@student.ac.kr / student3")
    print("\n" + "=" * 60)
    print("🌐 서버 주소: http://localhost:5000")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

