# backend/app/repositories/__init__.py
"""
Repositories 패키지

모든 데이터 접근 클래스들을 관리
"""

from .base_repository import BaseRepository
from .note_repository import NoteRepository

__all__ = ['BaseRepository', 'NoteRepository']