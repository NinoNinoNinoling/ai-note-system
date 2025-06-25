# backend/app/repositories/note_repository.py
"""
NoteRepository - 노트 모델 전용 데이터 접근 클래스

노트 검색, 태그 필터링 등 노트 특화 기능 제공
"""

from .base_repository import BaseRepository
from models.note import Note
from sqlalchemy import or_, func, desc
import logging

logger = logging.getLogger(__name__)


class NoteRepository(BaseRepository):
    """노트 전용 레포지토리"""
    
    def __init__(self):
        super().__init__(Note)
    
    def find_by_tags(self, tags):
        """
        태그로 노트 검색
        
        Args:
            tags: 태그 리스트 또는 단일 태그 문자열
        """
        try:
            if isinstance(tags, str):
                tags = [tags]
            
            # JSON 문자열에서 태그 검색 (Note 모델의 저장 방식에 맞춤)
            conditions = []
            for tag in tags:
                # JSON 배열에서 정확한 태그 매칭을 위해 따옴표 포함해서 검색
                tag_pattern = f'"{tag}"'
                conditions.append(self.model.tags.contains(tag_pattern))
            
            if conditions:
                return self.model.query.filter(or_(*conditions)).all()
            else:
                return []
            
        except Exception as e:
            logger.error(f"Error finding notes by tags {tags}: {e}")
            raise
    
    def search_content(self, query):
        """
        제목과 내용에서 텍스트 검색
        
        Args:
            query: 검색어
        """
        try:
            search_term = f"%{query}%"
            
            return self.model.query.filter(
                or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term)
                )
            ).all()
            
        except Exception as e:
            logger.error(f"Error searching notes with query '{query}': {e}")
            raise
    
    def find_recent(self, limit=10):
        """최근 생성된 노트들"""
        try:
            return self.model.query.order_by(desc(self.model.created_at)).limit(limit).all()
        except Exception as e:
            logger.error(f"Error finding recent notes: {e}")
            raise
    
    def find_by_title_like(self, title_part):
        """제목에 특정 문자열이 포함된 노트들"""
        try:
            search_term = f"%{title_part}%"
            return self.model.query.filter(self.model.title.ilike(search_term)).all()
        except Exception as e:
            logger.error(f"Error finding notes by title like '{title_part}': {e}")
            raise
    
    def get_all_tags(self):
        """모든 노트의 태그들을 중복 제거해서 반환"""
        try:
            notes = self.find_all()
            all_tags = set()
            
            for note in notes:
                # Note 모델의 get_tags() 메소드 사용
                note_tags = note.get_tags() if hasattr(note, 'get_tags') else []
                if note_tags:
                    all_tags.update(note_tags)
            
            return sorted(list(all_tags))
            
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            raise
    
    def get_notes_by_date_range(self, start_date, end_date):
        """날짜 범위로 노트 검색"""
        try:
            return self.model.query.filter(
                self.model.created_at >= start_date,
                self.model.created_at <= end_date
            ).order_by(desc(self.model.created_at)).all()
            
        except Exception as e:
            logger.error(f"Error finding notes by date range: {e}")
            raise
    
    def get_note_stats(self):
        """노트 통계 정보"""
        try:
            total_notes = self.count()
            total_tags = len(self.get_all_tags())
            
            # 가장 최근 노트
            recent_note = self.find_recent(1)
            last_created = recent_note[0].created_at if recent_note else None
            
            return {
                "total_notes": total_notes,
                "total_tags": total_tags,
                "last_created": last_created.isoformat() if last_created else None
            }
            
        except Exception as e:
            logger.error(f"Error getting note stats: {e}")
            raise
    
    def search_combined(self, query, tags=None, limit=50):
        """
        통합 검색 (제목/내용 + 태그)
        
        Args:
            query: 검색어 (선택사항)
            tags: 태그 리스트 (선택사항)
            limit: 결과 개수 제한
        """
        try:
            base_query = self.model.query
            
            conditions = []
            
            # 텍스트 검색
            if query:
                search_term = f"%{query}%"
                conditions.append(
                    or_(
                        self.model.title.ilike(search_term),
                        self.model.content.ilike(search_term)
                    )
                )
            
            # 태그 검색 (JSON 문자열에서 검색)
            if tags:
                if isinstance(tags, str):
                    tags = [tags]
                    
                tag_conditions = []
                for tag in tags:
                    # JSON 배열에서 정확한 태그 매칭
                    tag_pattern = f'"{tag}"'
                    tag_conditions.append(self.model.tags.contains(tag_pattern))
                
                if tag_conditions:
                    conditions.append(or_(*tag_conditions))
            
            # 조건 적용
            if conditions:
                if len(conditions) == 1:
                    base_query = base_query.filter(conditions[0])
                else:
                    base_query = base_query.filter(or_(*conditions))
            
            # 최신순 정렬 및 제한
            return base_query.order_by(desc(self.model.created_at)).limit(limit).all()
            
        except Exception as e:
            logger.error(f"Error in combined search: {e}")
            raise