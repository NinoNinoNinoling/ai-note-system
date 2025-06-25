# backend/app/controllers/note_controller.py
"""
NoteController - 노트 API 컨트롤러

깔끔하게 분리된 API 엔드포인트들
BaseController + NoteService를 활용
"""

from flask import request
from app.controllers.base_controller import BaseController
from app.services.note_service import NoteService
import logging

logger = logging.getLogger(__name__)


class NoteController(BaseController):
    """노트 API 컨트롤러"""
    
    def __init__(self):
        self.service = NoteService()
    
    def get_notes(self):
        """
        GET /api/notes
        노트 목록 조회 (페이지네이션 지원)
        """
        self.log_request("get_notes")
        
        try:
            # 쿼리 파라미터 추출
            limit = request.args.get('limit', type=int)
            offset = request.args.get('offset', type=int)
            
            # 노트 조회
            notes = self.service.get_all_notes(limit=limit, offset=offset)
            
            # 응답 데이터 구성
            response_data = {
                "notes": [self._note_to_dict(note) for note in notes],
                "total": len(notes),
                "limit": limit,
                "offset": offset
            }
            
            return self.success_response(
                data=response_data,
                message=f"{len(notes)}개의 노트를 조회했습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="노트 목록 조회 실패",
                details=str(e),
                status=500
            )
    
    def get_note(self, note_id):
        """
        GET /api/notes/<id>
        특정 노트 조회
        """
        self.log_request(f"get_note/{note_id}")
        
        try:
            note = self.service.get_note_by_id(note_id)
            
            return self.success_response(
                data={"note": self._note_to_dict(note)},
                message="노트를 조회했습니다"
            )
            
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="노트 조회 실패",
                details=str(e),
                status=500
            )
    
    def create_note(self):
        """
        POST /api/notes
        새 노트 생성
        """
        self.log_request("create_note")
        
        try:
            # JSON 데이터 검증
            data, error = self.get_json_data(['title', 'content'])
            if error:
                return error
            
            # 노트 생성
            note = self.service.create_note(
                title=data['title'],
                content=data['content'],
                tags=data.get('tags')  # 선택사항
            )
            
            return self.success_response(
                data={"note": self._note_to_dict(note)},
                message="노트가 성공적으로 생성되었습니다",
                status=201
            )
            
        except ValueError as e:
            return self.validation_error("input", str(e))
        except Exception as e:
            return self.error_response(
                message="노트 생성 실패",
                details=str(e),
                status=500
            )
    
    def update_note(self, note_id):
        """
        PUT /api/notes/<id>
        노트 업데이트
        """
        self.log_request(f"update_note/{note_id}")
        
        try:
            # JSON 데이터 검증 (모든 필드 선택사항)
            data, error = self.get_json_data()
            if error:
                return error
            
            # 최소한 하나의 필드는 있어야 함
            allowed_fields = ['title', 'content', 'tags']
            update_fields = {k: v for k, v in data.items() if k in allowed_fields}
            
            if not update_fields:
                return self.validation_error(
                    "update_data", 
                    f"업데이트할 필드가 필요합니다: {allowed_fields}"
                )
            
            # 노트 업데이트
            note = self.service.update_note(note_id, **update_fields)
            
            return self.success_response(
                data={"note": self._note_to_dict(note)},
                message="노트가 성공적으로 업데이트되었습니다"
            )
            
        except ValueError as e:
            if "찾을 수 없습니다" in str(e):
                return self.not_found_error("노트")
            return self.validation_error("input", str(e))
        except Exception as e:
            return self.error_response(
                message="노트 업데이트 실패",
                details=str(e),
                status=500
            )
    
    def delete_note(self, note_id):
        """
        DELETE /api/notes/<id>
        노트 삭제
        """
        self.log_request(f"delete_note/{note_id}")
        
        try:
            success = self.service.delete_note(note_id)
            
            if success:
                return self.success_response(
                    data={"deleted_id": note_id},
                    message="노트가 성공적으로 삭제되었습니다"
                )
            else:
                return self.error_response(
                    message="노트 삭제 실패",
                    status=500
                )
                
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="노트 삭제 실패",
                details=str(e),
                status=500
            )
    
    def search_notes(self):
        """
        POST /api/notes/search
        노트 검색
        """
        self.log_request("search_notes")
        
        try:
            # JSON 데이터가 없는 경우도 허용 (빈 검색 = 최근 노트)
            data = request.get_json() or {}
            
            query = data.get('query')
            tags = data.get('tags')
            limit = data.get('limit', 50)
            
            # 검색 실행
            results = self.service.search_notes(
                query=query,
                tags=tags,
                limit=limit
            )
            
            return self.success_response(
                data={
                    "notes": [self._note_to_dict(note) for note in results],
                    "total": len(results),
                    "query": query,
                    "tags": tags
                },
                message=f"{len(results)}개의 노트를 찾았습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="노트 검색 실패",
                details=str(e),
                status=500
            )
    
    def get_tags(self):
        """
        GET /api/notes/tags
        모든 태그 목록
        """
        self.log_request("get_tags")
        
        try:
            tags = self.service.get_all_tags()
            
            return self.success_response(
                data={
                    "tags": tags,
                    "total": len(tags)
                },
                message=f"{len(tags)}개의 태그를 조회했습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="태그 목록 조회 실패",
                details=str(e),
                status=500
            )
    
    def get_notes_by_tag(self, tag):
        """
        GET /api/notes/tags/<tag>
        특정 태그의 노트들
        """
        self.log_request(f"get_notes_by_tag/{tag}")
        
        try:
            notes = self.service.get_notes_by_tag(tag)
            
            return self.success_response(
                data={
                    "notes": [self._note_to_dict(note) for note in notes],
                    "total": len(notes),
                    "tag": tag
                },
                message=f"'{tag}' 태그로 {len(notes)}개의 노트를 찾았습니다"
            )
            
        except ValueError as e:
            return self.validation_error("tag", str(e))
        except Exception as e:
            return self.error_response(
                message="태그별 노트 조회 실패",
                details=str(e),
                status=500
            )
    
    def get_stats(self):
        """
        GET /api/notes/stats
        노트 통계
        """
        self.log_request("get_stats")
        
        try:
            stats = self.service.get_note_stats()
            
            return self.success_response(
                data=stats,
                message="통계를 조회했습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="통계 조회 실패",
                details=str(e),
                status=500
            )
    
    def _note_to_dict(self, note):
        """
        Note 모델을 딕셔너리로 변환
        
        프론트엔드가 사용하기 쉬운 형태로 변환
        """
        try:
            # Note 모델의 get_tags() 메소드 사용
            note_tags = note.get_tags() if hasattr(note, 'get_tags') else []
            
            return {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "tags": note_tags,
                "created_at": note.created_at.isoformat() if note.created_at else None,
                "updated_at": note.updated_at.isoformat() if note.updated_at else None,
                # 추가 메타데이터
                "content_length": len(note.content) if note.content else 0,
                "tag_count": len(note_tags)
            }
        except Exception as e:
            logger.error(f"Error converting note to dict: {e}")
            # 최소한의 정보라도 반환
            return {
                "id": getattr(note, 'id', None),
                "title": getattr(note, 'title', ''),
                "content": getattr(note, 'content', ''),
                "tags": [],
                "created_at": None,
                "updated_at": None,
                "content_length": 0,
                "tag_count": 0
            }