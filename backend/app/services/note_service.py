# backend/app/services/note_service.py
"""
NoteService - 노트 관련 비즈니스 로직

노트 생성/수정/삭제, 검색, 태그 처리 등의 비즈니스 규칙을 담당
"""

from app.repositories.note_repository import NoteRepository
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NoteService:
    """노트 비즈니스 로직 서비스"""
    
    def __init__(self):
        self.repository = NoteRepository()
    
    def create_note(self, title, content, tags=None):
        """
        새 노트 생성
        
        Args:
            title: 노트 제목
            content: 노트 내용
            tags: 태그 리스트 (없으면 자동 추출)
        """
        try:
            # 입력값 검증
            if not title or not title.strip():
                raise ValueError("제목은 필수입니다")
            
            if not content or not content.strip():
                raise ValueError("내용은 필수입니다")
            
            # 제목 정리
            title = title.strip()
            if len(title) > 200:
                raise ValueError("제목은 200자를 초과할 수 없습니다")
            
            # 태그 처리
            if tags is None:
                tags = self.extract_tags_from_content(content)
            else:
                tags = self.validate_tags(tags)
            
            # 노트 생성
            note = self.repository.create(
                title=title,
                content=content,
                tags=tags
            )
            
            logger.info(f"Created note '{title}' with {len(tags)} tags")
            return note
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            raise Exception(f"노트 생성 중 오류가 발생했습니다: {str(e)}")
    
    def get_note_by_id(self, note_id):
        """ID로 노트 조회"""
        try:
            if not note_id or note_id <= 0:
                raise ValueError("유효하지 않은 노트 ID입니다")
            
            note = self.repository.find_by_id(note_id)
            if not note:
                raise ValueError(f"노트 ID {note_id}를 찾을 수 없습니다")
            
            return note
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting note {note_id}: {e}")
            raise Exception(f"노트 조회 중 오류가 발생했습니다: {str(e)}")
    
    def update_note(self, note_id, title=None, content=None, tags=None):
        """노트 업데이트"""
        try:
            # 기존 노트 조회
            note = self.get_note_by_id(note_id)
            
            # 업데이트할 데이터 준비
            update_data = {}
            
            if title is not None:
                title = title.strip()
                if not title:
                    raise ValueError("제목은 비워둘 수 없습니다")
                if len(title) > 200:
                    raise ValueError("제목은 200자를 초과할 수 없습니다")
                update_data['title'] = title
            
            if content is not None:
                if not content.strip():
                    raise ValueError("내용은 비워둘 수 없습니다")
                update_data['content'] = content
                
                # 내용이 변경되면 태그도 자동 추출 (tags가 명시적으로 제공되지 않은 경우)
                if tags is None:
                    update_data['tags'] = self.extract_tags_from_content(content)
            
            if tags is not None:
                update_data['tags'] = self.validate_tags(tags)
            
            # 변경사항이 없으면 그냥 반환
            if not update_data:
                return note
            
            # 업데이트 실행
            updated_note = self.repository.update(note, **update_data)
            
            logger.info(f"Updated note {note_id}: {list(update_data.keys())}")
            return updated_note
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating note {note_id}: {e}")
            raise Exception(f"노트 업데이트 중 오류가 발생했습니다: {str(e)}")
    
    def delete_note(self, note_id):
        """노트 삭제"""
        try:
            # 노트 존재 확인
            note = self.get_note_by_id(note_id)
            
            # 삭제 실행
            success = self.repository.delete(note)
            
            if success:
                logger.info(f"Deleted note {note_id}: '{note.title}'")
            
            return success
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            raise Exception(f"노트 삭제 중 오류가 발생했습니다: {str(e)}")
    
    def get_all_notes(self, limit=None, offset=None):
        """모든 노트 조회 (페이지네이션 지원)"""
        try:
            notes = self.repository.find_all(limit=limit, offset=offset)
            return notes
        except Exception as e:
            logger.error(f"Error getting all notes: {e}")
            raise Exception(f"노트 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    def search_notes(self, query=None, tags=None, limit=50):
        """노트 검색"""
        try:
            if not query and not tags:
                # 검색어가 없으면 최근 노트 반환
                return self.repository.find_recent(limit)
            
            # 통합 검색 실행
            results = self.repository.search_combined(
                query=query,
                tags=tags,
                limit=limit
            )
            
            logger.info(f"Search completed: query='{query}', tags={tags}, results={len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise Exception(f"노트 검색 중 오류가 발생했습니다: {str(e)}")
    
    def get_all_tags(self):
        """모든 태그 목록"""
        try:
            return self.repository.get_all_tags()
        except Exception as e:
            logger.error(f"Error getting all tags: {e}")
            raise Exception(f"태그 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    def get_notes_by_tag(self, tag):
        """특정 태그의 노트들"""
        try:
            if not tag or not tag.strip():
                raise ValueError("태그는 필수입니다")
            
            tag = tag.strip().lower()
            notes = self.repository.find_by_tags([tag])
            
            return notes
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting notes by tag '{tag}': {e}")
            raise Exception(f"태그별 노트 조회 중 오류가 발생했습니다: {str(e)}")
    
    def get_note_stats(self):
        """노트 통계"""
        try:
            stats = self.repository.get_note_stats()
            
            # 추가 통계 계산
            recent_notes = self.repository.find_recent(10)
            stats['recent_activity'] = len([
                note for note in recent_notes 
                if note.created_at > datetime.now() - timedelta(days=7)
            ])
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting note stats: {e}")
            raise Exception(f"통계 조회 중 오류가 발생했습니다: {str(e)}")
    
    def extract_tags_from_content(self, content):
        """
        마크다운 내용에서 태그 자동 추출
        
        #태그 형태의 해시태그를 찾아서 추출
        """
        try:
            if not content:
                return []
            
            # #태그 패턴 찾기 (한글, 영문, 숫자, 하이픈, 언더스코어 허용)
            tag_pattern = r'#([가-힣A-Za-z0-9_-]+)'
            matches = re.findall(tag_pattern, content)
            
            # 중복 제거, 소문자 변환, 정렬
            tags = sorted(list(set(tag.lower() for tag in matches)))
            
            return tags
            
        except Exception as e:
            logger.error(f"Error extracting tags from content: {e}")
            return []
    
    def validate_tags(self, tags):
        """태그 유효성 검증"""
        try:
            if not tags:
                return []
            
            if isinstance(tags, str):
                tags = [tags]
            
            validated_tags = []
            
            for tag in tags:
                if not isinstance(tag, str):
                    continue
                
                tag = tag.strip().lower()
                
                # 빈 태그 제거
                if not tag:
                    continue
                
                # 길이 제한
                if len(tag) > 50:
                    tag = tag[:50]
                
                # 특수문자 정리 (한글, 영문, 숫자, 하이픈, 언더스코어만 허용)
                tag = re.sub(r'[^가-힣A-Za-z0-9_-]', '', tag)
                
                if tag and tag not in validated_tags:
                    validated_tags.append(tag)
            
            # 태그 개수 제한 (최대 10개)
            if len(validated_tags) > 10:
                validated_tags = validated_tags[:10]
                logger.warning("태그 개수가 10개를 초과하여 자동으로 제한되었습니다")
            
            return sorted(validated_tags)
            
        except Exception as e:
            logger.error(f"Error validating tags: {e}")
            return []