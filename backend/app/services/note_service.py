# backend/app/services/note_service.py
"""
NoteService - 디버깅 강화 버전

모든 DB 조회 및 비즈니스 로직을 상세하게 로깅
"""

from app.repositories.note_repository import NoteRepository
import re
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class NoteService:
    """노트 비즈니스 로직 서비스"""
    
    def __init__(self):
        print("🔧 NoteService 초기화 중...")
        self.repository = NoteRepository()
        self.rag_available = False
        self.rag_chain = None
        
        # RAG 시스템 초기화
        self._initialize_rag()
        print("✅ NoteService 초기화 완료")
    
    def _initialize_rag(self):
        """RAG 시스템 초기화"""
        try:
            from chains.rag_chain import rag_chain, RAG_AVAILABLE
            
            if RAG_AVAILABLE and rag_chain and rag_chain.is_available():
                self.rag_chain = rag_chain
                self.rag_available = True
                logger.info("✅ NoteService RAG 시스템 연결 성공")
            else:
                logger.warning("⚠️ NoteService RAG 시스템 사용 불가")
                
        except ImportError as e:
            logger.warning(f"⚠️ NoteService RAG 시스템 임포트 실패: {e}")
    
    def get_all_notes(self, limit=None, offset=None):
        """모든 노트 조회 (페이지네이션 지원) - 디버깅 강화"""
        
        print(f"\n{'='*60}")
        print(f"🗄️ NoteService.get_all_notes() 실행")
        print(f"{'='*60}")
        print(f"📋 Parameters: limit={limit}, offset={offset}")
        
        try:
            print("🔍 Step 1: Repository.find_all() 호출 중...")
            
            # Repository에서 데이터 조회
            notes = self.repository.find_all(limit=limit, offset=offset)
            
            print(f"🔍 Step 1 완료:")
            print(f"   - 조회된 노트 수: {len(notes) if notes else 0}")
            print(f"   - Notes 타입: {type(notes)}")
            
            if notes is None:
                print("⚠️ Repository에서 None 반환!")
                return []
            
            if len(notes) == 0:
                print("⚠️ Repository에서 빈 리스트 반환!")
                print("🔍 DB에 노트가 없거나 쿼리 조건에 맞는 노트가 없음")
                return notes
            
            # 첫 번째 노트 상세 정보 출력
            if len(notes) > 0:
                first_note = notes[0]
                print(f"🔍 첫 번째 노트 상세:")
                print(f"   - ID: {getattr(first_note, 'id', 'No ID')}")
                print(f"   - Title: {getattr(first_note, 'title', 'No Title')}")
                print(f"   - Content Length: {len(getattr(first_note, 'content', '')) if getattr(first_note, 'content', None) else 0}")
                print(f"   - Created At: {getattr(first_note, 'created_at', 'No Date')}")
                print(f"   - Tags: {getattr(first_note, 'tags_list', 'No Tags')}")
                print(f"   - Note Type: {type(first_note)}")
                
                # 노트 객체의 모든 속성 출력
                try:
                    print(f"🔍 Note Attributes: {dir(first_note)}")
                    print(f"🔍 Note Dict: {first_note.__dict__ if hasattr(first_note, '__dict__') else 'No __dict__'}")
                except Exception as attr_error:
                    print(f"⚠️ 속성 확인 실패: {attr_error}")
            
            print(f"✅ NoteService.get_all_notes() 완료: {len(notes)}개 노트 반환")
            print(f"{'='*60}\n")
            
            return notes
            
        except Exception as e:
            print(f"❌ NoteService.get_all_notes() 에러:")
            print(f"   - 에러 타입: {type(e).__name__}")
            print(f"   - 에러 메시지: {str(e)}")
            
            import traceback
            print(f"❌ 전체 트레이스백:")
            traceback.print_exc()
            
            logger.error(f"Error getting all notes: {e}")
            raise Exception(f"노트 목록 조회 중 오류가 발생했습니다: {str(e)}")
    
    def get_note_by_id(self, note_id):
        """ID로 노트 조회"""
        print(f"\n🔍 NoteService.get_note_by_id({note_id}) 실행")
        
        try:
            if not note_id or note_id <= 0:
                raise ValueError("유효하지 않은 노트 ID입니다")
            
            note = self.repository.find_by_id(note_id)
            
            if not note:
                print(f"❌ 노트 ID {note_id} 찾을 수 없음")
                raise ValueError(f"노트 ID {note_id}를 찾을 수 없습니다")
            
            print(f"✅ 노트 발견: '{note.title}' (ID: {note.id})")
            return note
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error getting note by id {note_id}: {e}")
            raise Exception(f"노트 조회 중 오류가 발생했습니다: {str(e)}")
    
    def create_note(self, title, content, tags=None):
        """새 노트 생성"""
        print(f"\n📝 NoteService.create_note() 실행")
        print(f"   - Title: {title}")
        print(f"   - Content Length: {len(content) if content else 0}")
        print(f"   - Tags: {tags}")
        
        try:
            # 입력값 검증
            if not title or not title.strip():
                raise ValueError("제목은 필수입니다")
            
            if not content or not content.strip():
                raise ValueError("내용은 필수입니다")
            
            # 제목과 내용 정리
            title = title.strip()
            content = content.strip()
            
            # 태그 처리
            if tags is None:
                tags = self.extract_tags_from_content(content)
            else:
                tags = self.validate_tags(tags)
            
            print(f"🔍 처리된 태그: {tags}")
            
            # Repository를 통해 저장
            note = self.repository.create(
                title=title,
                content=content,
                tags=tags
            )
            
            print(f"✅ 노트 생성 완료: ID {note.id}")
            
            # RAG 인덱스 업데이트
            self._update_rag_index(note)
            
            logger.info(f"Created new note: '{title}' (ID: {note.id})")
            return note
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error creating note: {e}")
            raise Exception(f"노트 생성 중 오류가 발생했습니다: {str(e)}")
    
    def extract_tags_from_content(self, content):
        """내용에서 태그 추출 (#태그 형식)"""
        if not content:
            return []
        
        # #태그 패턴 추출
        tags = re.findall(r'#(\w+)', content)
        # 중복 제거 및 소문자 변환
        unique_tags = list(set(tag.lower() for tag in tags))
        
        return unique_tags
    
    def validate_tags(self, tags):
        """태그 유효성 검증"""
        if not tags:
            return []
        
        if isinstance(tags, str):
            # 쉼표 구분 문자열인 경우
            tags = [tag.strip() for tag in tags.split(',')]
        
        # 빈 태그 제거 및 소문자 변환
        validated_tags = []
        for tag in tags:
            if isinstance(tag, str) and tag.strip():
                clean_tag = tag.strip().lower()
                if clean_tag not in validated_tags:
                    validated_tags.append(clean_tag)
        
        return validated_tags
    
    def _update_rag_index(self, note):
        """RAG 인덱스 업데이트"""
        if self.rag_available and self.rag_chain:
            try:
                success = self.rag_chain.add_note(note.id, note.title, note.content)
                if success:
                    logger.info(f"✅ 노트 {note.id} RAG 인덱스 업데이트 완료")
                else:
                    logger.warning(f"⚠️ 노트 {note.id} RAG 인덱스 업데이트 실패")
            except Exception as e:
                logger.error(f"❌ RAG 인덱스 업데이트 오류: {e}")
    
    # 다른 메서드들도 기본 로깅 유지
    def search_notes(self, query=None, tags=None, limit=50):
        """노트 검색"""
        print(f"\n🔍 NoteService.search_notes() 실행")
        print(f"   - Query: {query}")
        print(f"   - Tags: {tags}")
        print(f"   - Limit: {limit}")
        
        try:
            if not query and not tags:
                # 검색어가 없으면 최근 노트 반환
                results = self.repository.find_recent(limit)
            else:
                # 통합 검색 실행
                results = self.repository.search_combined(
                    query=query,
                    tags=tags,
                    limit=limit
                )
            
            print(f"✅ 검색 완료: {len(results)}개 노트 발견")
            logger.info(f"Search completed: query='{query}', tags={tags}, results={len(results)}")
            return results
            
        except Exception as e:
            logger.error(f"Error searching notes: {e}")
            raise Exception(f"노트 검색 중 오류가 발생했습니다: {str(e)}")
        
    def delete_note(self, note_id):
        """노트 삭제"""
        print(f"\n🗑️ NoteService.delete_note({note_id}) 실행")

        try:
            if not note_id or note_id <= 0:
                raise ValueError("유효하지 않은 노트 ID입니다")
            
            note = self.repository.find_by_id(note_id)
            if not note:
                print(f"❌ 노트 ID {note_id} 찾을 수 없음")
                raise ValueError(f"노트 ID {note_id}를 찾을 수 없습니다")
            
            print(f"🔍 삭제할 노트: ID={note.id}, Title='{note.title}'")
            
            success = self.repository.delete(note_id)
            if success:
                print(f"✅ 노트 ID {note_id} 삭제 성공")
                logger.info(f"Deleted note ID: {note_id}")
                return True
            else:
                print(f"❌ 노트 ID {note_id} 삭제 실패")
                return False

        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error deleting note {note_id}: {e}")
            raise Exception(f"노트 삭제 중 오류가 발생했습니다: {str(e)}")
