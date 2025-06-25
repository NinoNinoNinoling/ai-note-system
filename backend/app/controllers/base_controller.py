# backend/app/controllers/base_controller.py
"""
완전히 보완된 BaseController

✅ 추가사항:
1. 에러 처리 개선
2. 로깅 기능 강화
3. 공통 유틸리티 메서드 추가
4. 응답 형식 표준화
"""

from flask import request, jsonify
from datetime import datetime
import logging
import json

logger = logging.getLogger(__name__)


class BaseController:
    """기본 컨트롤러 클래스 - 공통 기능 제공"""
    
    def __init__(self):
        self.logger = logger
    
    # =========================
    # 요청 데이터 처리
    # =========================
    
    def get_json_data(self, required_fields=None):
        """
        JSON 데이터 추출 및 검증
        
        Args:
            required_fields: 필수 필드 리스트
            
        Returns:
            tuple: (data, error) - error가 None이면 성공
        """
        try:
            # Content-Type 확인
            if not request.is_json:
                return None, self.error_response(
                    message="JSON 데이터가 필요합니다",
                    details="Content-Type을 application/json으로 설정해주세요",
                    status=400
                )
            
            # JSON 파싱
            try:
                data = request.get_json()
            except Exception as parse_error:
                return None, self.error_response(
                    message="JSON 파싱 실패",
                    details=f"올바른 JSON 형식이 아닙니다: {str(parse_error)}",
                    status=400
                )
            
            if data is None:
                return None, self.error_response(
                    message="빈 JSON 데이터",
                    details="요청 본문이 비어있습니다",
                    status=400
                )
            
            # 필수 필드 검증
            if required_fields:
                missing_fields = []
                for field in required_fields:
                    if field not in data or data[field] is None:
                        missing_fields.append(field)
                    elif isinstance(data[field], str) and not data[field].strip():
                        missing_fields.append(f"{field} (빈 값)")
                
                if missing_fields:
                    return None, self.error_response(
                        message="필수 필드가 누락되었습니다",
                        details=f"누락된 필드: {', '.join(missing_fields)}",
                        status=400
                    )
            
            return data, None
            
        except Exception as e:
            logger.error(f"get_json_data 오류: {e}")
            return None, self.error_response(
                message="요청 처리 실패",
                details=str(e),
                status=500
            )
    
    def get_query_params(self, **defaults):
        """
        쿼리 파라미터 추출 (GET 요청용)
        
        Args:
            **defaults: 기본값들
            
        Returns:
            dict: 파라미터 딕셔너리
        """
        params = {}
        
        for key, default_value in defaults.items():
            if isinstance(default_value, int):
                params[key] = request.args.get(key, default_value, type=int)
            elif isinstance(default_value, bool):
                params[key] = request.args.get(key, str(default_value)).lower() in ('true', '1', 'yes')
            else:
                params[key] = request.args.get(key, default_value, type=str)
        
        return params
    
    # =========================
    # 응답 생성
    # =========================
    
    def success_response(self, data=None, message="성공", status=200):
        """성공 응답 생성"""
        response_data = {
            "success": True,
            "message": message,
            "timestamp": self._get_timestamp()
        }
        
        if data is not None:
            response_data["data"] = data
        
        return jsonify(response_data), status
    
    def error_response(self, message="오류가 발생했습니다", details=None, status=500):
        """에러 응답 생성"""
        response_data = {
            "success": False,
            "error": message,
            "timestamp": self._get_timestamp()
        }
        
        if details:
            response_data["details"] = details
        
        logger.error(f"Error: {message} (Status: {status}) - Details: {details}")
        
        return jsonify(response_data), status
    
    def not_found_error(self, resource_name="리소스"):
        """404 에러 응답 생성"""
        return self.error_response(
            message=f"{resource_name}을(를) 찾을 수 없습니다",
            details="요청한 ID에 해당하는 데이터가 존재하지 않습니다",
            status=404
        )
    
    def validation_error(self, field_name, message):
        """유효성 검사 에러 응답 생성"""
        return self.error_response(
            message="입력 데이터 검증 실패",
            details=f"{field_name}: {message}",
            status=400
        )
    
    # =========================
    # 로깅 및 유틸리티
    # =========================
    
    def log_request(self, action_name):
        """요청 로깅"""
        client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
        user_agent = request.headers.get('User-Agent', 'Unknown')
        
        logger.info(f"Action: {action_name} | IP: {client_ip} | Method: {request.method} | Path: {request.path}")
        
        # 개발 모드에서는 더 자세한 로깅
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Headers: {dict(request.headers)}")
            if request.is_json:
                try:
                    logger.debug(f"JSON Data: {request.get_json()}")
                except:
                    logger.debug("JSON Data: 파싱 실패")
    
    def log_response(self, action_name, success, response_time=None):
        """응답 로깅"""
        status = "SUCCESS" if success else "FAILED"
        time_info = f" ({response_time:.2f}ms)" if response_time else ""
        
        logger.info(f"Action: {action_name} | Status: {status}{time_info}")
    
    def _get_timestamp(self):
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
    
    # =========================
    # 데이터 변환 유틸리티
    # =========================
    
    def paginate_response(self, items, page, per_page, total_count):
        """페이지네이션 응답 생성"""
        return {
            "items": items,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total_count,
                "pages": (total_count + per_page - 1) // per_page,
                "has_prev": page > 1,
                "has_next": page * per_page < total_count
            }
        }
    
    def sanitize_string(self, value, max_length=None):
        """문자열 정제"""
        if not isinstance(value, str):
            return str(value) if value is not None else ""
        
        # 기본 정제
        cleaned = value.strip()
        
        # 길이 제한
        if max_length and len(cleaned) > max_length:
            cleaned = cleaned[:max_length].rstrip()
        
        return cleaned
    
    def validate_positive_integer(self, value, field_name):
        """양의 정수 검증"""
        try:
            num = int(value)
            if num <= 0:
                raise ValueError(f"{field_name}은(는) 양의 정수여야 합니다")
            return num
        except (ValueError, TypeError):
            raise ValueError(f"{field_name}은(는) 유효한 양의 정수여야 합니다")
    
    def validate_required_fields(self, data, fields):
        """필수 필드 검증"""
        missing = []
        for field in fields:
            if field not in data:
                missing.append(field)
            elif data[field] is None:
                missing.append(f"{field} (null)")
            elif isinstance(data[field], str) and not data[field].strip():
                missing.append(f"{field} (빈 값)")
        
        if missing:
            raise ValueError(f"필수 필드 누락: {', '.join(missing)}")
        
        return True
    
    # =========================
    # 에러 핸들링 데코레이터
    # =========================
    
    def handle_exceptions(self, func):
        """예외 처리 데코레이터"""
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except ValueError as e:
                return self.error_response(
                    message="입력 오류",
                    details=str(e),
                    status=400
                )
            except PermissionError as e:
                return self.error_response(
                    message="권한 없음",
                    details=str(e),
                    status=403
                )
            except FileNotFoundError as e:
                return self.error_response(
                    message="파일을 찾을 수 없습니다",
                    details=str(e),
                    status=404
                )
            except Exception as e:
                logger.exception(f"Unexpected error in {func.__name__}")
                return self.error_response(
                    message="서버 내부 오류",
                    details="예상치 못한 오류가 발생했습니다",
                    status=500
                )
        
        return wrapper
    
    # =========================
    # 보안 관련
    # =========================
    
    def check_content_type(self, expected_type="application/json"):
        """Content-Type 확인"""
        if request.content_type != expected_type:
            return self.error_response(
                message="잘못된 Content-Type",
                details=f"Expected: {expected_type}, Got: {request.content_type}",
                status=415
            )
        return None
    
    def check_method(self, allowed_methods):
        """HTTP 메서드 확인"""
        if request.method not in allowed_methods:
            return self.error_response(
                message="허용되지 않은 HTTP 메서드",
                details=f"Allowed: {', '.join(allowed_methods)}, Got: {request.method}",
                status=405
            )
        return None