# backend/utils/response_utils.py - 간단한 응답 헬퍼
"""
API 응답 표준화 유틸리티

과제용 심플 버전
"""

from flask import jsonify
from datetime import datetime
from typing import Any, Dict, List, Optional


def success_response(data: Any = None, message: str = "성공", status_code: int = 200) -> tuple:
    """성공 응답 생성"""
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if data is not None:
        response["data"] = data
    
    return jsonify(response), status_code


def error_response(message: str = "오류가 발생했습니다", details: str = None, status_code: int = 400) -> tuple:
    """오류 응답 생성"""
    response = {
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }
    
    if details:
        response["details"] = details
    
    return jsonify(response), status_code


def paginated_response(items: List[Any], total: int, page: int = 1, per_page: int = 20, message: str = None) -> tuple:
    """페이지네이션 응답 생성"""
    if not message:
        message = f"{len(items)}개 항목 조회"
    
    data = {
        "items": items,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": (total + per_page - 1) // per_page
        }
    }
    
    return success_response(data, message)


def search_response(query: str, results: List[Any], total: int = None, filters: Dict = None) -> tuple:
    """검색 결과 응답 생성"""
    if total is None:
        total = len(results)
    
    data = {
        "query": query,
        "results": results,
        "total": total
    }
    
    if filters:
        data["filters"] = filters
    
    message = f"'{query}'에 대한 {total}개 결과"
    return success_response(data, message)


def validate_required_fields(data: Dict, required_fields: List[str]) -> Optional[str]:
    """필수 필드 검증"""
    missing_fields = []
    
    for field in required_fields:
        if field not in data or not data[field]:
            missing_fields.append(field)
    
    if missing_fields:
        return f"필수 필드가 누락되었습니다: {', '.join(missing_fields)}"
    
    return None


def safe_get_json(request, required_fields: List[str] = None) -> tuple:
    """안전한 JSON 데이터 추출"""
    try:
        data = request.get_json()
        
        if not data:
            return None, "JSON 데이터가 필요합니다"
        
        if required_fields:
            error_msg = validate_required_fields(data, required_fields)
            if error_msg:
                return None, error_msg
        
        return data, None
        
    except Exception as e:
        return None, f"JSON 파싱 오류: {str(e)}"


def format_note_response(note, include_processed: bool = False) -> Dict:
    """노트 응답 형식 표준화"""
    response = note.to_dict()
    
    if include_processed:
        from utils.markdown_utils import process_markdown_content
        
        # 마크다운 처리 결과 추가
        processed = process_markdown_content(note.content)
        response.update({
            "html_content": processed["html"],
            "preview": processed["preview"],
            "word_count": processed["word_count"],
            "extracted_tags": processed["tags"],
            "linked_notes": processed["links"],
            "headers": processed["headers"]
        })
    
    return response