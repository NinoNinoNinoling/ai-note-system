# backend/app/controllers/base_controller.py
"""
BaseController - 모든 컨트롤러의 기본 클래스

공통 응답 처리, 에러 핸들링, 로깅 등을 담당
"""

from flask import jsonify, request
from datetime import datetime
import logging

# 로거 설정
logger = logging.getLogger(__name__)


class BaseController:
    """모든 컨트롤러의 기본 클래스"""
    
    def success_response(self, data=None, message="Success", status=200):
        """
        성공 응답 표준화
        
        Args:
            data: 응답 데이터
            message: 성공 메시지  
            status: HTTP 상태 코드
        """
        response = {
            "success": True,
            "message": message,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.info(f"Success: {message} (Status: {status})")
        return jsonify(response), status
    
    def error_response(self, message="Error occurred", details=None, status=400):
        """
        에러 응답 표준화
        
        Args:
            message: 에러 메시지
            details: 상세 에러 정보
            status: HTTP 상태 코드
        """
        response = {
            "success": False,
            "error": message,
            "details": details,
            "timestamp": datetime.now().isoformat()
        }
        
        logger.error(f"Error: {message} (Status: {status}) - Details: {details}")
        return jsonify(response), status
    
    def validation_error(self, field, message):
        """입력값 검증 에러"""
        return self.error_response(
            message=f"Validation error: {field}",
            details=message,
            status=400
        )
    
    def not_found_error(self, resource="Resource"):
        """404 에러"""
        return self.error_response(
            message=f"{resource} not found",
            status=404
        )
    
    def get_json_data(self, required_fields=None):
        """
        JSON 요청 데이터 검증 및 추출
        
        Args:
            required_fields: 필수 필드 리스트
            
        Returns:
            tuple: (data, error_response)
            error_response가 None이면 성공
        """
        try:
            data = request.get_json()
            
            if not data:
                return None, self.validation_error("request_body", "JSON data required")
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return None, self.validation_error(
                        "required_fields", 
                        f"Missing required fields: {missing_fields}"
                    )
            
            return data, None
            
        except Exception as e:
            return None, self.error_response(
                message="Invalid JSON format",
                details=str(e),
                status=400
            )
    
    def log_request(self, endpoint_name):
        """요청 로깅"""
        logger.info(f"Request to {endpoint_name}: {request.method} {request.url}")
        if request.get_json():
            logger.debug(f"Request data: {request.get_json()}")