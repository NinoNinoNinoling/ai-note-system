# backend/app/repositories/note_repository.py
"""
NoteRepository - 완전한 디버깅 강화 버전

노트 모델 전용 데이터 접근 클래스
모든 DB 조회와 쿼리를 상세하게 로깅
"""

from .base_repository import BaseRepository
from models.note import Note
from sqlalchemy import or_, func, desc, text
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class NoteRepository(BaseRepository):
    """노트 전용 레포지토리"""
    
    def __init__(self):
        super().__init__(Note)
        print("🗄️ NoteRepository 초기화 완료")
    
    def find_all(self, limit=None, offset=None):
        """모든 노트 조회 - 디버깅 강화"""
        
        print(f"\n{'='*60}")
        print(f"🗄️ NoteRepository.find_all() 실행")
        print(f"{'='*60}")
        print(f"📋 Parameters: limit={limit}, offset={offset}")
        
        try:
            print("🔍 Step 1: DB 연결 상태 확인...")
            
            # DB 연결 확인
            try:
                # 간단한 쿼리로 DB 연결 테스트
                test_result = self.session.execute(text("SELECT 1")).fetchone()
                print(f"✅ DB 연결 성공: {test_result}")
            except Exception as db_error:
                print(f"❌ DB 연결 실패: {db_error}")
                raise
            
            print("🔍 Step 2: 노트 테이블 존재 확인...")
            
            # 테이블 존재 확인
            try:
                table_exists = self.session.execute(
                    text("SELECT name FROM sqlite_master WHERE type='table' AND name='notes'")
                ).fetchone()
                print(f"📊 Notes 테이블 존재: {table_exists is not None}")
                
                if table_exists:
                    # 테이블 구조 확인
                    columns = self.session.execute(text("PRAGMA table_info(notes)")).fetchall()
                    print(f"📊 Notes 테이블 컬럼: {[col[1] for col in columns]}")
                    
                    # 전체 노트 개수 확인
                    total_count = self.session.execute(text("SELECT COUNT(*) FROM notes")).fetchone()[0]
                    print(f"📊 DB 내 총 노트 수: {total_count}")
                    
                    if total_count > 0:
                        # 첫 번째 노트 확인 (원시 SQL)
                        first_note_raw = self.session.execute(text("SELECT * FROM notes LIMIT 1")).fetchone()
                        print(f"📊 첫 번째 노트 (Raw): {first_note_raw}")
                        
                        # 모든 노트의 ID와 제목 확인
                        all_notes_brief = self.session.execute(text("SELECT id, title FROM notes LIMIT 5")).fetchall()
                        print(f"📊 노트 목록 (처음 5개): {all_notes_brief}")
                else:
                    print("❌ Notes 테이블이 존재하지 않습니다!")
                    return []
                    
            except Exception as table_error:
                print(f"❌ 테이블 확인 실패: {table_error}")
                # 계속 진행
            
            print("🔍 Step 3: SQLAlchemy ORM 쿼리 실행...")
            
            # 실제 ORM 쿼리 실행
            query = self.model.query
            print(f"📊 Base Query: {query}")
            
            # 정렬 추가 (최신순)
            query = query.order_by(desc(self.model.created_at))
            print(f"📊 Query with Order: {query}")
            
            if offset:
                query = query.offset(offset)
                print(f"📊 Query with Offset: {query}")
            
            if limit:
                query = query.limit(limit)
                print(f"📊 Query with Limit: {query}")
            
            # 최종 SQL 출력 (가능하면)
            try:
                print(f"📊 Final SQL: {query.statement.compile(compile_kwargs={'literal_binds': True})}")
            except:
                print(f"📊 Final SQL: {query.statement}")
            
            print("🔍 Step 4: 쿼리 실행 및 결과 확인...")
            
            # 쿼리 실행
            results = query.all()
            
            print(f"🔍 Step 4 완료:")
            print(f"   - 결과 타입: {type(results)}")
            print(f"   - 결과 개수: {len(results) if results else 0}")
            
            if results:
                print(f"   - 첫 번째 결과 타입: {type(results[0])}")
                
                # 첫 번째 노트의 모든 속성 확인
                first_note = results[0]
                try:
                    print(f"📊 첫 번째 노트 상세:")
                    print(f"   - ID: {first_note.id}")
                    print(f"   - Title: {first_note.title}")
                    print(f"   - Content: {first_note.content[:100]}..." if first_note.content else "None")
                    print(f"   - Created: {first_note.created_at}")
                    print(f"   - Updated: {first_note.updated_at}")
                    print(f"   - Tags: {first_note.tags}")
                    
                    # 태그 메서드 테스트
                    if hasattr(first_note, 'get_tags'):
                        tags_list = first_note.get_tags()
                        print(f"   - Tags List: {tags_list}")
                    
                    # 전체 노트 ID 목록 출력
                    all_ids = [note.id for note in results]
                    print(f"📊 모든 노트 ID: {all_ids[:10]}...")  # 처음 10개만
                    
                except Exception as attr_error:
                    print(f"⚠️ 노트 속성 접근 실패: {attr_error}")
            else:
                print("⚠️ ORM 쿼리 결과가 비어있습니다!")
                
                # 다시 원시 SQL로 확인
                print("🔍 원시 SQL로 재확인...")
                raw_results = self.session.execute(text("SELECT * FROM notes")).fetchall()
                print(f"📊 원시 SQL 결과: {len(raw_results)}개")
                
                if raw_results:
                    print(f"📊 첫 번째 원시 결과: {raw_results[0]}")
                    print("❌ ORM과 원시 SQL 결과가 다름! 모델 매핑 문제 의심됨")
                else:
                    print("📊 원시 SQL도 결과 없음 - DB가 실제로 비어있음")
            
            print(f"✅ NoteRepository.find_all() 완료")
            print(f"{'='*60}\n")
            
            return results
            
        except Exception as e:
            print(f"❌ NoteRepository.find_all() 에러:")
            print(f"   - 에러 타입: {type(e).__name__}")
            print(f"   - 에러 메시지: {str(e)}")
            
            import traceback
            print(f"❌ 전체 트레이스백:")
            traceback.print_exc()
            
            logger.error(f"Error finding all Notes: {e}")
            raise
    
    def find_by_id(self, note_id):
        """ID로 노트 조회 - 디버깅 추가"""
        print(f"\n🔍 NoteRepository.find_by_id({note_id}) 실행")
        
        try:
            # BaseRepository의 find_by_id 사용
            result = super().find_by_id(note_id)
            
            if result:
                print(f"✅ 노트 발견: '{result.title}' (ID: {result.id})")
            else:
                print(f"❌ 노트 ID {note_id} 찾을 수 없음")
            
            return result
            
        except Exception as e:
            print(f"❌ 노트 조회 에러: {e}")
            logger.error(f"Error finding note by id {note_id}: {e}")
            raise
    
    def find_by_tags(self, tags):
        """태그로 노트 검색"""
        print(f"\n🏷️ NoteRepository.find_by_tags({tags}) 실행")
        
        try:
            if isinstance(tags, str):
                tags = [tags]
            
            print(f"🔍 검색할 태그들: {tags}")
            
            # JSON 문자열에서 태그 검색 (Note 모델의 저장 방식에 맞춤)
            conditions = []
            for tag in tags:
                # JSON 배열에서 정확한 태그 매칭을 위해 따옴표 포함해서 검색
                tag_pattern = f'"{tag}"'
                conditions.append(self.model.tags.contains(tag_pattern))
                print(f"🔍 태그 '{tag}' 검색 패턴: {tag_pattern}")
            
            if conditions:
                results = self.model.query.filter(or_(*conditions)).all()
                print(f"✅ 태그 검색 완료: {len(results)}개 노트 발견")
                return results
            else:
                print("⚠️ 검색할 태그가 없음")
                return []
            
        except Exception as e:
            print(f"❌ 태그 검색 에러: {e}")
            logger.error(f"Error finding notes by tags {tags}: {e}")
            raise
    
    def search_content(self, query):
        """제목과 내용에서 텍스트 검색"""
        print(f"\n🔍 NoteRepository.search_content('{query}') 실행")
        
        try:
            search_term = f"%{query}%"
            print(f"🔍 검색 패턴: {search_term}")
            
            results = self.model.query.filter(
                or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term)
                )
            ).order_by(desc(self.model.created_at)).all()
            
            print(f"✅ 내용 검색 완료: {len(results)}개 노트 발견")
            return results
            
        except Exception as e:
            print(f"❌ 내용 검색 에러: {e}")
            logger.error(f"Error searching notes with query '{query}': {e}")
            raise
    
    def find_recent(self, limit=10):
        """최근 생성된 노트들"""
        print(f"\n📅 NoteRepository.find_recent({limit}) 실행")
        
        try:
            results = self.model.query.order_by(desc(self.model.created_at)).limit(limit).all()
            print(f"✅ 최근 노트 조회 완료: {len(results)}개")
            
            if results:
                print(f"📊 가장 최근 노트: '{results[0].title}' ({results[0].created_at})")
            
            return results
            
        except Exception as e:
            print(f"❌ 최근 노트 조회 에러: {e}")
            logger.error(f"Error finding recent notes: {e}")
            raise
    
    def find_by_title_like(self, title_part):
        """제목에 특정 문자열이 포함된 노트들"""
        print(f"\n📝 NoteRepository.find_by_title_like('{title_part}') 실행")
        
        try:
            search_term = f"%{title_part}%"
            results = self.model.query.filter(self.model.title.ilike(search_term)).all()
            
            print(f"✅ 제목 검색 완료: {len(results)}개 노트 발견")
            return results
            
        except Exception as e:
            print(f"❌ 제목 검색 에러: {e}")
            logger.error(f"Error finding notes by title like '{title_part}': {e}")
            raise
    
    def get_all_tags(self):
        """모든 노트의 태그들을 중복 제거해서 반환"""
        print(f"\n🏷️ NoteRepository.get_all_tags() 실행")
        
        try:
            notes = self.find_all()
            all_tags = set()
            
            print(f"🔍 {len(notes)}개 노트에서 태그 추출 중...")
            
            for note in notes:
                # Note 모델의 get_tags() 메소드 사용
                note_tags = note.get_tags() if hasattr(note, 'get_tags') else []
                if note_tags:
                    all_tags.update(note_tags)
                    print(f"📊 노트 '{note.title}' 태그: {note_tags}")
            
            sorted_tags = sorted(list(all_tags))
            print(f"✅ 전체 태그 추출 완료: {len(sorted_tags)}개 태그")
            print(f"📊 태그 목록: {sorted_tags}")
            
            return sorted_tags
            
        except Exception as e:
            print(f"❌ 태그 목록 조회 에러: {e}")
            logger.error(f"Error getting all tags: {e}")
            raise
    
    def get_notes_by_date_range(self, start_date, end_date):
        """날짜 범위로 노트 검색"""
        print(f"\n📅 NoteRepository.get_notes_by_date_range({start_date}, {end_date}) 실행")
        
        try:
            results = self.model.query.filter(
                self.model.created_at >= start_date,
                self.model.created_at <= end_date
            ).order_by(desc(self.model.created_at)).all()
            
            print(f"✅ 날짜 범위 검색 완료: {len(results)}개 노트 발견")
            return results
            
        except Exception as e:
            print(f"❌ 날짜 범위 검색 에러: {e}")
            logger.error(f"Error finding notes by date range: {e}")
            raise
    
    def get_note_stats(self):
        """노트 통계 정보"""
        print(f"\n📊 NoteRepository.get_note_stats() 실행")
        
        try:
            total_notes = self.count()
            total_tags = len(self.get_all_tags())
            
            # 가장 최근 노트
            recent_note = self.find_recent(1)
            last_created = recent_note[0].created_at if recent_note else None
            
            # 7일 내 생성된 노트 수
            week_ago = datetime.now() - timedelta(days=7)
            recent_notes_count = self.model.query.filter(
                self.model.created_at >= week_ago
            ).count()
            
            # 평균 내용 길이
            all_notes = self.find_all()
            avg_content_length = 0
            if all_notes:
                total_length = sum(len(note.content) if note.content else 0 for note in all_notes)
                avg_content_length = total_length / len(all_notes)
            
            stats = {
                "total_notes": total_notes,
                "total_tags": total_tags,
                "last_created": last_created.isoformat() if last_created else None,
                "recent_notes_count": recent_notes_count,
                "avg_content_length": round(avg_content_length, 2)
            }
            
            print(f"✅ 통계 생성 완료: {stats}")
            return stats
            
        except Exception as e:
            print(f"❌ 통계 생성 에러: {e}")
            logger.error(f"Error getting note stats: {e}")
            raise
    
    def search_combined(self, query=None, tags=None, limit=50):
        """통합 검색 (텍스트 + 태그)"""
        print(f"\n🔍 NoteRepository.search_combined(query='{query}', tags={tags}, limit={limit}) 실행")
        
        try:
            base_query = self.model.query
            conditions = []
            
            # 텍스트 검색 조건
            if query and query.strip():
                search_term = f"%{query.strip()}%"
                text_condition = or_(
                    self.model.title.ilike(search_term),
                    self.model.content.ilike(search_term)
                )
                conditions.append(text_condition)
                print(f"🔍 텍스트 검색 조건 추가: {search_term}")
            
            # 태그 검색 조건
            if tags:
                if isinstance(tags, str):
                    tags = [tags]
                
                tag_conditions = []
                for tag in tags:
                    tag_pattern = f'"{tag}"'
                    tag_conditions.append(self.model.tags.contains(tag_pattern))
                
                if tag_conditions:
                    conditions.append(or_(*tag_conditions))
                    print(f"🔍 태그 검색 조건 추가: {tags}")
            
            # 조건 적용
            if conditions:
                if len(conditions) == 1:
                    final_query = base_query.filter(conditions[0])
                else:
                    # 여러 조건은 AND로 결합
                    final_query = base_query.filter(*conditions)
            else:
                # 조건이 없으면 최근 노트 반환
                final_query = base_query
            
            # 정렬 및 제한
            results = final_query.order_by(desc(self.model.created_at)).limit(limit).all()
            
            print(f"✅ 통합 검색 완료: {len(results)}개 노트 발견")
            
            if results:
                print(f"📊 첫 번째 결과: '{results[0].title}'")
            
            return results
            
        except Exception as e:
            print(f"❌ 통합 검색 에러: {e}")
            logger.error(f"Error in combined search: {e}")
            raise
    
    def count(self):
        """전체 노트 개수"""
        try:
            count = self.model.query.count()
            print(f"📊 전체 노트 개수: {count}")
            return count
        except Exception as e:
            print(f"❌ 개수 조회 에러: {e}")
            logger.error(f"Error counting notes: {e}")
            raise
        
    def delete(self, note_id):
        """노트 삭제 - 디버깅 포함"""
        print(f"\n🗑️ NoteRepository.delete({note_id}) 실행")

        try:
            note = self.model.query.get(note_id)
            if not note:
                print(f"❌ 노트 ID {note_id}를 찾을 수 없음")
                return False
            
            print(f"🔍 삭제할 노트: ID={note.id}, Title='{note.title}'")

            self.session.delete(note)
            self.session.commit()

            print(f"✅ 노트 ID {note_id} 삭제 완료")
            logger.info(f"Deleted note: ID={note_id}")
            return True

        except Exception as e:
            print(f"❌ 노트 삭제 에러: {e}")
            logger.error(f"Error deleting note ID {note_id}: {e}")
            self.session.rollback()
            raise
