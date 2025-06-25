# backend/app/routes/chat.py
"""
Chat 라우트 - ChatController 사용 버전

이제 라우팅만 담당하고 모든 로직은 ChatController가 처리
"""

from flask import Blueprint
from app.controllers.chat_controller import ChatController

# Blueprint 생성
chat_bp = Blueprint('chat', __name__)

# 컨트롤러 인스턴스 생성
controller = ChatController()


# ====== 기본 채팅 ======

@chat_bp.route('/', methods=['POST'])
def chat():
    """기본 AI 채팅"""
    return controller.basic_chat()


@chat_bp.route('/test', methods=['GET'])
def test_claude():
    """Claude API 연결 테스트"""
    return controller.test_claude_connection()


# ====== RAG 기반 채팅 ======

@chat_bp.route('/rag', methods=['POST'])
def chat_with_rag():
    """RAG 기반 지능형 채팅"""
    return controller.rag_chat()


@chat_bp.route('/rag/status', methods=['GET'])
def rag_status():
    """RAG 시스템 상태 확인"""
    return controller.get_rag_status()


@chat_bp.route('/rag/rebuild', methods=['POST'])
def rebuild_rag_index():
    """RAG 인덱스 재구축"""
    return controller.rebuild_rag_index()


# ====== 채팅 히스토리 ======

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """채팅 히스토리 조회"""
    return controller.get_chat_history()


@chat_bp.route('/history', methods=['DELETE'])
def clear_chat_history():
    """채팅 히스토리 삭제"""
    return controller.clear_chat_history()


# ====== 통계 및 정보 ======

@chat_bp.route('/stats', methods=['GET'])
def get_chat_stats():
    """채팅 통계 정보"""
    return controller.get_chat_stats()