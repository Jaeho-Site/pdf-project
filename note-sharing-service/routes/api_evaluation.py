# -*- coding: utf-8 -*-
"""
필기 평가 API 라우트
"""
from flask import Blueprint, request, jsonify, session
from services.database_service import DatabaseService
from services.pdf_service import PDFService
from services.gemini_service import GeminiService
from services.evaluation_scheduler import EvaluationScheduler
from utils.auth_middleware import check_auth
import os

api_evaluation_bp = Blueprint('api_evaluation', __name__)
db = DatabaseService()
pdf_service = PDFService()

@api_evaluation_bp.route('/courses/<course_id>/week/<int:week>/evaluate', methods=['POST', 'OPTIONS'])
def trigger_evaluation(course_id, week):
    """수동으로 평가 트리거 (교수만)"""
    if request.method == 'OPTIONS':
        return '', 200
    
    auth_result = check_auth(required_role='professor')
    if auth_result:
        return auth_result
    
    user_id = request.headers.get('X-User-ID')
    
    course = db.get_course_by_id(course_id)
    if not course:
        return jsonify({'success': False, 'message': '존재하지 않는 강의입니다.'}), 404
    
    if course['professor_id'] != user_id:
        return jsonify({'success': False, 'message': '본인의 강의만 평가할 수 있습니다.'}), 403
    
    # Gemini API 키 확인
    gemini_api_key = os.getenv('GEMINI_API_KEY')
    if not gemini_api_key:
        return jsonify({
            'success': False, 
            'message': 'Gemini API 키가 설정되지 않았습니다.'
        }), 500
    
    try:
        scheduler = EvaluationScheduler(gemini_api_key=gemini_api_key)
        scheduler.evaluate_now(course_id=course_id, week=week)
        
        return jsonify({
            'success': True,
            'message': f'{week}주차 필기 평가가 시작되었습니다.'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'평가 중 오류가 발생했습니다: {str(e)}'
        }), 500

