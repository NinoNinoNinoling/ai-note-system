# backend/app/routes/__init__.py
"""
API Routes 패키지

이 패키지는 Flask Blueprint들을 포함합니다:
- notes.py: 노트 관련 API
- chat.py: AI 채팅 관련 API
"""

from .notes import notes_bp
from .chat import chat_bp

__all__ = ['notes_bp', 'chat_bp']