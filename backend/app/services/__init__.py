# backend/app/services/__init__.py
"""
Services 패키지

모든 비즈니스 로직 서비스들을 관리
"""

from .note_service import NoteService

__all__ = ['NoteService']