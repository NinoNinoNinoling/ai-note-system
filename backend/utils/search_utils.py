# backend/utils/search_utils.py - 검색 헬퍼 유틸
"""
노트 검색 관련 유틸리티
"""

import re
from typing import List, Dict, Any
from models.note import Note
from utils.markdown_utils import markdown_processor


class NoteSearcher:
    """노트 검색기"""
    
    def __init__(self):
        self.processor = markdown_processor
    
    def search_notes(self, query: str, filters: Dict = None) -> List[Note]:
        """통합 노트 검색"""
        if not query or len(query.strip()) < 2:
            return []
        
        query = query.strip()
        
        # 기본 쿼리 구성
        search_query = Note.query
        
        # 텍스트 검색 (제목, 내용)
        search_query = search_query.filter(
            Note.title.ilike(f'%{query}%') | 
            Note.content.ilike(f'%{query}%')
        )
        
        # 필터 적용
        if filters:
            search_query = self._apply_filters(search_query, filters)
        
        # 정렬 (관련도순 - 제목 매치 우선)
        results = search_query.all()
        return self._sort_by_relevance(results, query)
    
    def _apply_filters(self, query, filters: Dict):
        """검색 필터 적용"""
        
        # 태그 필터
        if 'tags' in filters and filters['tags']:
            for tag in filters['tags']:
                query = query.filter(Note.tags.ilike(f'%"{tag}"%'))
        
        # 날짜 필터
        if 'date_from' in filters and filters['date_from']:
            query = query.filter(Note.created_at >= filters['date_from'])
        
        if 'date_to' in filters and filters['date_to']:
            query = query.filter(Note.created_at <= filters['date_to'])
        
        return query
    
    def _sort_by_relevance(self, notes: List[Note], query: str) -> List[Note]:
        """관련도순 정렬"""
        query_lower = query.lower()
        
        def calculate_score(note):
            score = 0
            title_lower = note.title.lower()
            content_lower = note.content.lower()
            
            # 제목 정확 매치 (높은 점수)
            if query_lower == title_lower:
                score += 100
            elif query_lower in title_lower:
                score += 50
            
            # 내용 매치
            content_matches = content_lower.count(query_lower)
            score += content_matches * 5
            
            # 태그 매치
            tags = note.get_tags()
            for tag in tags:
                if query_lower in tag.lower():
                    score += 20
            
            # 최신 노트 약간 우대
            if note.updated_at:
                days_old = (Note.query.first().updated_at - note.updated_at).days
                score += max(0, 10 - days_old)
            
            return score
        
        return sorted(notes, key=calculate_score, reverse=True)
    
    def search_by_tags(self, tags: List[str]) -> List[Note]:
        """태그로 노트 검색"""
        if not tags:
            return []
        
        query = Note.query
        
        for tag in tags:
            query = query.filter(Note.tags.ilike(f'%"{tag}"%'))
        
        return query.order_by(Note.updated_at.desc()).all()
    
    def find_similar_notes(self, note: Note, limit: int = 5) -> List[Note]:
        """유사한 노트 찾기 (태그, 키워드 기반)"""
        similar_notes = []
        note_tags = set(note.get_tags())
        
        if not note_tags:
            return []
        
        # 같은 태그를 가진 노트들 찾기
        candidates = Note.query.filter(
            Note.id != note.id  # 자기 자신 제외
        ).all()
        
        scored_notes = []
        for candidate in candidates:
            candidate_tags = set(candidate.get_tags())
            
            # 공통 태그 개수로 유사도 계산
            common_tags = note_tags.intersection(candidate_tags)
            if common_tags:
                similarity_score = len(common_tags) / len(note_tags.union(candidate_tags))
                scored_notes.append((candidate, similarity_score))
        
        # 유사도순 정렬
        scored_notes.sort(key=lambda x: x[1], reverse=True)
        
        return [note for note, score in scored_notes[:limit]]
    
    def get_search_suggestions(self, partial_query: str) -> Dict[str, List[str]]:
        """검색 자동완성 제안"""
        if len(partial_query) < 2:
            return {"titles": [], "tags": [], "keywords": []}
        
        partial_lower = partial_query.lower()
        
        # 노트 제목 제안
        title_suggestions = []
        notes = Note.query.limit(100).all()  # 최신 100개만
        
        for note in notes:
            if partial_lower in note.title.lower():
                title_suggestions.append(note.title)
        
        # 태그 제안
        tag_suggestions = []
        all_tags = Note.get_all_tags()
        
        for tag in all_tags:
            if partial_lower in tag.lower():
                tag_suggestions.append(tag)
        
        # 키워드 제안 (자주 사용되는 단어들)
        keyword_suggestions = self._extract_common_keywords(partial_lower)
        
        return {
            "titles": title_suggestions[:5],
            "tags": tag_suggestions[:5], 
            "keywords": keyword_suggestions[:5]
        }
    
    def _extract_common_keywords(self, partial_query: str) -> List[str]:
        """자주 사용되는 키워드 추출"""
        common_keywords = [
            "python", "javascript", "vue", "react", "flask", "django",
            "html", "css", "api", "database", "sql", "ai", "ml",
            "langchain", "claude", "openai", "markdown", "git",
            "학습", "정리", "프로젝트", "아이디어", "메모", "계획"
        ]
        
        return [kw for kw in common_keywords if partial_query in kw.lower()]
    
    def highlight_search_results(self, notes: List[Note], query: str) -> List[Dict]:
        """검색 결과에 하이라이트 적용"""
        highlighted_notes = []
        search_terms = query.split()
        
        for note in notes:
            # 제목 하이라이트
            highlighted_title = note.title
            for term in search_terms:
                highlighted_title = self.processor.highlight_search_terms(
                    highlighted_title, [term]
                )
            
            # 내용 미리보기 하이라이트
            preview = self.processor.create_preview(note.content, 200)
            for term in search_terms:
                preview = self.processor.highlight_search_terms(preview, [term])
            
            highlighted_notes.append({
                "id": note.id,
                "title": note.title,
                "highlighted_title": highlighted_title,
                "preview": preview,
                "tags": note.get_tags(),
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "updated_at": note.updated_at.isoformat() if note.updated_at else None
            })
        
        return highlighted_notes


# 전역 검색기 인스턴스
note_searcher = NoteSearcher()


# 편의 함수들
def quick_search(query: str, limit: int = 20) -> List[Dict]:
    """빠른 검색 (하이라이트 포함)"""
    notes = note_searcher.search_notes(query)[:limit]
    return note_searcher.highlight_search_results(notes, query)


def advanced_search(query: str, tags: List[str] = None, date_from: str = None, date_to: str = None) -> List[Dict]:
    """고급 검색"""
    filters = {}
    
    if tags:
        filters['tags'] = tags
    if date_from:
        filters['date_from'] = date_from
    if date_to:
        filters['date_to'] = date_to
    
    notes = note_searcher.search_notes(query, filters)
    return note_searcher.highlight_search_results(notes, query)