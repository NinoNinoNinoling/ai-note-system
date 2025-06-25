# backend/app/routes/chat.py
"""
Chat 라우트 - 깔끔한 버전

이제 라우팅만 담당하고 모든 로직은 ChatController가 처리
RAG 시스템 완전 연결!
"""

from flask import Blueprint
from app.controllers.chat_controller import ChatController

# Blueprint 생성
chat_bp = Blueprint('chat', __name__)

# 컨트롤러 인스턴스 생성
controller = ChatController()


# ====== 기본 AI 채팅 ======

@chat_bp.route('/chat', methods=['POST'])
def basic_chat():
    """기본 AI 채팅"""
    return controller.basic_chat()


@chat_bp.route('/chat/test', methods=['GET'])
def test_claude_connection():
    """Claude API 연결 테스트"""
    return controller.test_claude_connection()


# ====== RAG 기반 지능형 채팅 (🔥 과제 핵심!) ======

@chat_bp.route('/chat/rag', methods=['POST'])
def rag_chat():
    """RAG 기반 지능형 채팅"""
    return controller.rag_chat()


@chat_bp.route('/chat/rag/status', methods=['GET'])
def get_rag_status():
    """RAG 시스템 상태 확인"""
    return controller.get_rag_status()


@chat_bp.route('/chat/rag/rebuild', methods=['POST'])
def rebuild_rag_index():
    """RAG 인덱스 재구축"""
    return controller.rebuild_rag_index()


# ====== 채팅 히스토리 관리 ======

@chat_bp.route('/chat/history', methods=['GET'])
def get_chat_history():
    """채팅 히스토리 조회"""
    return controller.get_chat_history()


@chat_bp.route('/chat/history', methods=['DELETE'])
def clear_chat_history():
    """채팅 히스토리 삭제"""
    return controller.clear_chat_history()


@chat_bp.route('/chat/stats', methods=['GET'])
def get_chat_stats():
    """채팅 통계 정보"""
    return controller.get_chat_stats()


# ====== 개발용 유틸리티 ======

@chat_bp.route('/chat/debug', methods=['GET'])
def debug_chat_system():
    """채팅 시스템 디버그 정보"""
    try:
        # RAG 상태
        rag_info = controller.service.get_rag_status()
        
        # Claude API 상태
        claude_info = controller.service.test_claude_connection()
        
        # 채팅 히스토리 통계
        from models.note import ChatHistory
        total_chats = ChatHistory.query.count()
        
        debug_info = {
            "chat_system": {
                "status": "active",
                "total_chats": total_chats
            },
            "rag_system": rag_info,
            "claude_api": claude_info,
            "available_endpoints": [
                "POST /api/chat - 기본 AI 채팅",
                "POST /api/chat/rag - RAG 기반 지능형 채팅",
                "GET /api/chat/test - Claude API 테스트",
                "GET /api/chat/rag/status - RAG 상태 확인",
                "POST /api/chat/rag/rebuild - RAG 인덱스 재구축",
                "GET /api/chat/history - 채팅 히스토리",
                "DELETE /api/chat/history - 히스토리 삭제",
                "GET /api/chat/stats - 채팅 통계"
            ]
        }
        
        return controller.success_response(
            data=debug_info,
            message="채팅 시스템 디버그 정보"
        )
        
    except Exception as e:
        return controller.error_response(
            message="디버그 정보 조회 실패",
            details=str(e),
            status=500
        )