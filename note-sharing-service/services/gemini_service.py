# -*- coding: utf-8 -*-
"""
Gemini API를 사용한 필기 품질 평가 서비스
"""
import os
import google.generativeai as genai
from typing import Dict, List, Optional
from PIL import Image
import base64
import io

class GeminiService:
    """Gemini API를 사용한 필기 평가 서비스"""
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Gemini 서비스 초기화
        
        Args:
            api_key: Gemini API 키 (환경변수 GEMINI_API_KEY에서도 읽을 수 있음)
        """
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("Gemini API 키가 설정되지 않았습니다. GEMINI_API_KEY 환경변수를 설정하거나 api_key를 전달하세요.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')
    
    def evaluate_note_quality(self, image_path: str, page_num: int, 
                             course_name: str = "", week: int = 0) -> Dict:
        """
        필기 페이지의 품질을 평가
        
        Args:
            image_path: 필기 페이지 이미지 경로
            page_num: 페이지 번호
            course_name: 강의명 (선택)
            week: 주차 (선택)
            
        Returns:
            {
                'overall_score': float,  # 전체 점수 (0-10)
                'readability': float,     # 가독성 점수 (0-10)
                'completeness': float,    # 완성도 점수 (0-10)
                'organization': float,    # 정리 상태 점수 (0-10)
                'feedback': str,          # 피드백 메시지
                'strengths': List[str],  # 강점 리스트
                'improvements': List[str] # 개선점 리스트
            }
        """
        try:
            # 이미지 로드
            image = Image.open(image_path)
            
            # 프롬프트 구성
            prompt = f"""다음은 대학 강의 필기 페이지입니다. 이 필기의 품질을 평가해주세요.

평가 기준:
1. 가독성 (Readability): 글씨가 읽기 쉬운가? 정리되어 있는가?
2. 완성도 (Completeness): 핵심 내용이 빠짐없이 포함되어 있는가?
3. 정리 상태 (Organization): 내용이 논리적으로 정리되어 있는가? 구조가 명확한가?

각 항목을 0-10점으로 평가하고, 전체 점수(0-10)를 계산해주세요.
또한 강점과 개선점을 구체적으로 제시해주세요.

응답 형식은 JSON으로 다음과 같이 작성해주세요:
{{
    "overall_score": 8.5,
    "readability": 9.0,
    "completeness": 8.0,
    "organization": 8.5,
    "feedback": "전반적으로 잘 정리된 필기입니다. 핵심 개념이 명확하게 정리되어 있습니다.",
    "strengths": ["글씨가 읽기 쉽다", "핵심 개념이 잘 정리되어 있다"],
    "improvements": ["일부 예시를 추가하면 더 좋을 것 같다"]
}}
"""
            
            # Gemini API 호출
            response = self.model.generate_content([prompt, image])
            
            # 응답 파싱
            response_text = response.text.strip()
            
            # JSON 추출 (마크다운 코드 블록 제거)
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            import json
            result = json.loads(response_text)
            
            # 기본값 설정
            return {
                'overall_score': float(result.get('overall_score', 0)),
                'readability': float(result.get('readability', 0)),
                'completeness': float(result.get('completeness', 0)),
                'organization': float(result.get('organization', 0)),
                'feedback': result.get('feedback', ''),
                'strengths': result.get('strengths', []),
                'improvements': result.get('improvements', [])
            }
            
        except Exception as e:
            print(f"Gemini 평가 오류 (페이지 {page_num}): {e}")
            # 오류 시 기본값 반환
            return {
                'overall_score': 0.0,
                'readability': 0.0,
                'completeness': 0.0,
                'organization': 0.0,
                'feedback': f'평가 중 오류가 발생했습니다: {str(e)}',
                'strengths': [],
                'improvements': []
            }
    
    def evaluate_material(self, material_id: str, thumbnail_paths: List[str]) -> Dict:
        """
        전체 필기본을 평가 (모든 페이지의 평균 점수)
        
        Args:
            material_id: 자료 ID
            thumbnail_paths: 썸네일 이미지 경로 리스트
            
        Returns:
            {
                'material_id': str,
                'overall_score': float,  # 전체 평균 점수
                'readability': float,
                'completeness': float,
                'organization': float,
                'page_scores': List[Dict],  # 페이지별 점수
                'feedback': str,
                'strengths': List[str],
                'improvements': List[str]
            }
        """
        page_scores = []
        total_readability = 0
        total_completeness = 0
        total_organization = 0
        all_strengths = []
        all_improvements = []
        
        for idx, thumbnail_path in enumerate(thumbnail_paths, start=1):
            page_result = self.evaluate_note_quality(thumbnail_path, idx)
            page_scores.append({
                'page_num': idx,
                **page_result
            })
            
            total_readability += page_result['readability']
            total_completeness += page_result['completeness']
            total_organization += page_result['organization']
            
            all_strengths.extend(page_result.get('strengths', []))
            all_improvements.extend(page_result.get('improvements', []))
        
        page_count = len(thumbnail_paths)
        if page_count == 0:
            return {
                'material_id': material_id,
                'overall_score': 0.0,
                'readability': 0.0,
                'completeness': 0.0,
                'organization': 0.0,
                'page_scores': [],
                'feedback': '평가할 페이지가 없습니다.',
                'strengths': [],
                'improvements': []
            }
        
        # 평균 계산
        avg_readability = total_readability / page_count
        avg_completeness = total_completeness / page_count
        avg_organization = total_organization / page_count
        overall_score = (avg_readability + avg_completeness + avg_organization) / 3
        
        # 중복 제거
        unique_strengths = list(set(all_strengths))
        unique_improvements = list(set(all_improvements))
        
        return {
            'material_id': material_id,
            'overall_score': round(overall_score, 2),
            'readability': round(avg_readability, 2),
            'completeness': round(avg_completeness, 2),
            'organization': round(avg_organization, 2),
            'page_scores': page_scores,
            'feedback': f'전체 {page_count}페이지를 평가했습니다. 평균 점수: {overall_score:.2f}점',
            'strengths': unique_strengths[:5],  # 상위 5개만
            'improvements': unique_improvements[:5]  # 상위 5개만
        }

