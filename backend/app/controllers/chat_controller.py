# backend/app/controllers/chat_controller.py
"""
ChatController - 채팅 API 컨트롤러 (415 에러 수정 버전)

GET 요청에서 BaseController 메서드 호출 최소화
"""

from app.controllers.base_controller import BaseController
from app.services.chat_service import ChatService
import logging

logger = logging.getLogger(__name__)


class ChatController(BaseController):
    """채팅 API 컨트롤러"""
    
    def __init__(self):
        self.service = ChatService()
    
    def basic_chat(self):
        """
        POST /api/
        기본 AI 채팅
        """
        try:
            # JSON 데이터 검증 (POST 요청이므로 안전)
            data, error = self.get_json_data(['message'])
            if error:
                return error
            
            message = data['message']
            save_history = data.get('save_history', True)
            
            # 채팅 처리
            result = self.service.basic_chat(message, save_history)
            
            return self.success_response(
                data=result,
                message="채팅 응답이 생성되었습니다"
            )
            
        except ValueError as e:
            return self.validation_error("message", str(e))
        except Exception as e:
            return self.error_response(
                message="채팅 처리 실패",
                details=str(e),
                status=500
            )
    
    def rag_chat(self):
        """
        POST /api/rag
        RAG 기반 지능형 채팅
        """
        try:
            # JSON 데이터 검증 (POST 요청이므로 안전)
            data, error = self.get_json_data(['message'])
            if error:
                return error
            
            message = data['message']
            save_history = data.get('save_history', True)
            
            # RAG 채팅 처리
            result = self.service.rag_chat(message, save_history)
            
            return self.success_response(
                data=result,
                message="RAG 기반 응답이 생성되었습니다"
            )
            
        except ValueError as e:
            return self.validation_error("message", str(e))
        except Exception as e:
            return self.error_response(
                message="RAG 채팅 처리 실패",
                details=str(e),
                status=500
            )
    
    def get_rag_status(self):
        """
        GET /api/rag/status
        RAG 시스템 상태 확인
        """
        try:
            # GET 요청이므로 log_request() 호출 제거
            status_info = self.service.get_rag_status()
            
            return self.success_response(
                data=status_info,
                message="RAG 시스템 상태를 조회했습니다"
            )
            
        except Exception as e:
            logger.error(f"RAG 상태 조회 실패: {str(e)}")
            return self.error_response(
                message="RAG 상태 조회 실패",
                details=str(e),
                status=500
            )
    
    def rebuild_rag_index(self):
        """
        POST /api/rag/rebuild
        RAG 인덱스 재구축
        """
        try:
            # POST 요청이지만 JSON 데이터는 선택적
            result = self.service.rebuild_rag_index()
            
            return self.success_response(
                data=result,
                message="RAG 인덱스가 재구축되었습니다"
            )
            
        except Exception as e:
            logger.error(f"RAG 인덱스 재구축 실패: {str(e)}")
            return self.error_response(
                message="RAG 인덱스 재구축 실패",
                details=str(e),
                status=500
            )
    
    def test_claude_connection(self):
        """
        GET /api/test
        Claude API 연결 테스트
        """
        try:
            # GET 요청이므로 log_request() 호출 제거
            test_result = self.service.test_claude_connection()
            
            if test_result["status"] == "success":
                return self.success_response(
                    data=test_result,
                    message="Claude API 연결 테스트 성공"
                )
            else:
                return self.error_response(
                    message="Claude API 연결 테스트 실패",
                    details=test_result.get("response", "Unknown error"),
                    status=503
                )
                
        except Exception as e:
            logger.error(f"Claude API 테스트 실패: {str(e)}")
            return self.error_response(
                message="Claude API 테스트 실패",
                details=str(e),
                status=500
            )
    
    def get_chat_history(self):
        """
        GET /api/history
        채팅 히스토리 조회
        """
        try:
            # GET 요청이므로 log_request() 호출 제거
            from flask import request
            limit = request.args.get('limit', 20, type=int)
            
            history = self.service.get_chat_history(limit)
            
            return self.success_response(
                data={
                    "chat_history": history,
                    "total": len(history),
                    "limit": limit
                },
                message=f"{len(history)}개의 채팅 기록을 조회했습니다"
            )
            
        except Exception as e:
            logger.error(f"채팅 히스토리 조회 실패: {str(e)}")
            return self.error_response(
                message="채팅 히스토리 조회 실패",
                details=str(e),
                status=500
            )
    
    def clear_chat_history(self):
        """
        DELETE /api/history
        채팅 히스토리 삭제
        """
        try:
            # DELETE 요청이므로 log_request() 호출 제거
            from models.note import ChatHistory
            from config.database import db
            
            deleted_count = ChatHistory.query.count()
            ChatHistory.query.delete()
            db.session.commit()
            
            return self.success_response(
                data={"deleted_count": deleted_count},
                message=f"{deleted_count}개의 채팅 기록이 삭제되었습니다"
            )
            
        except Exception as e:
            logger.error(f"채팅 히스토리 삭제 실패: {str(e)}")
            db.session.rollback()
            return self.error_response(
                message="채팅 히스토리 삭제 실패",
                details=str(e),
                status=500
            )
    
    def get_chat_stats(self):
        """
        GET /api/stats
        채팅 통계 정보
        """
        try:
            # GET 요청이므로 log_request() 호출 제거
            from models.note import ChatHistory
            from datetime import datetime, timedelta
            from config.database import db
            
            # 기본 통계
            total_chats = ChatHistory.query.count()
            
            # 최근 7일 채팅
            week_ago = datetime.now() - timedelta(days=7)
            recent_chats = ChatHistory.query.filter(
                ChatHistory.created_at >= week_ago
            ).count()
            
            # 모델별 사용 통계
            from sqlalchemy import func
            model_stats = db.session.query(
                ChatHistory.model_used,
                func.count(ChatHistory.id).label('count')
            ).group_by(ChatHistory.model_used).all()
            
            stats = {
                "total_chats": total_chats,
                "recent_chats_7d": recent_chats,
                "model_usage": [
                    {"model": model, "count": count}
                    for model, count in model_stats
                ],
                "rag_status": self.service.get_rag_status()["rag_status"]
            }
            
            return self.success_response(
                data=stats,
                message="채팅 통계를 조회했습니다"
            )
            
        except Exception as e:
            logger.error(f"채팅 통계 조회 실패: {str(e)}")
            return self.error_response(
                message="채팅 통계 조회 실패",
                details=str(e),
                status=500
            )