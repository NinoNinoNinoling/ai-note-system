# backend/app/routes/notes.py
"""
Notes 라우트 - 깔끔한 버전

이제 라우팅만 담당하고 모든 로직은 NoteController가 처리
"""

from flask import Blueprint, request
from app.controllers.note_controller import NoteController

# Blueprint 생성
notes_bp = Blueprint('notes', __name__)

# 컨트롤러 인스턴스 생성
controller = NoteController()


# ====== 노트 CRUD ======

@notes_bp.route('/notes', methods=['GET'])
def get_notes():
    """노트 목록 조회"""
    try:
        # 쿼리 파라미터 추출
        limit = request.args.get('limit', type=int)
        offset = request.args.get('offset', type=int)
        
        # 노트 조회
        notes = controller.service.get_all_notes(limit=limit, offset=offset)
        
        # 응답 데이터 구성
        response_data = {
            "notes": [controller._note_to_dict(note) for note in notes],
            "total": len(notes),
            "limit": limit,
            "offset": offset
        }
        
        return controller.success_response(
            data=response_data,
            message=f"{len(notes)}개의 노트를 조회했습니다"
        )
        
    except Exception as e:
        return controller.error_response(
            message="노트 목록 조회 실패",
            details=str(e),
            status=500
        )


@notes_bp.route('/notes/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """특정 노트 조회"""
    try:
        note = controller.service.get_note_by_id(note_id)
        
        return controller.success_response(
            data={"note": controller._note_to_dict(note)},
            message="노트를 조회했습니다"
        )
        
    except ValueError as e:
        return controller.not_found_error("노트")
    except Exception as e:
        return controller.error_response(
            message="노트 조회 실패",
            details=str(e),
            status=500
        )


@notes_bp.route('/notes', methods=['POST'])
def create_note():
    """새 노트 생성"""
    return controller.create_note()


@notes_bp.route('/notes/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """노트 업데이트"""
    return controller.update_note(note_id)


@notes_bp.route('/notes/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """노트 삭제"""
    try:
        success = controller.service.delete_note(note_id)
        
        if success:
            return controller.success_response(
                data={"deleted_id": note_id},
                message="노트가 성공적으로 삭제되었습니다"
            )
        else:
            return controller.error_response(
                message="노트 삭제 실패",
                status=500
            )
            
    except ValueError as e:
        return controller.not_found_error("노트")
    except Exception as e:
        return controller.error_response(
            message="노트 삭제 실패",
            details=str(e),
            status=500
        )


# ====== 검색 & 필터링 ======

@notes_bp.route('/notes/search', methods=['POST'])
def search_notes():
    """노트 검색"""
    try:
        # JSON 데이터가 없는 경우 빈 검색으로 처리 (최근 노트 반환)
        data = request.get_json() or {}
        
        query = data.get('query')
        tags = data.get('tags')
        limit = data.get('limit', 50)
        
        # 검색 실행
        results = controller.service.search_notes(
            query=query,
            tags=tags,
            limit=limit
        )
        
        return controller.success_response(
            data={
                "notes": [controller._note_to_dict(note) for note in results],
                "total": len(results),
                "query": query,
                "tags": tags
            },
            message=f"{len(results)}개의 노트를 찾았습니다"
        )
        
    except Exception as e:
        return controller.error_response(
            message="노트 검색 실패",
            details=str(e),
            status=500
        )


@notes_bp.route('/notes/tags', methods=['GET'])
def get_tags():
    """모든 태그 목록"""
    try:
        tags = controller.service.get_all_tags()
        
        return controller.success_response(
            data={
                "tags": tags,
                "total": len(tags)
            },
            message=f"{len(tags)}개의 태그를 조회했습니다"
        )
        
    except Exception as e:
        return controller.error_response(
            message="태그 목록 조회 실패",
            details=str(e),
            status=500
        )


@notes_bp.route('/notes/tags/<string:tag>', methods=['GET'])
def get_notes_by_tag(tag):
    """특정 태그의 노트들"""
    try:
        notes = controller.service.get_notes_by_tag(tag)
        
        return controller.success_response(
            data={
                "notes": [controller._note_to_dict(note) for note in notes],
                "total": len(notes),
                "tag": tag
            },
            message=f"'{tag}' 태그로 {len(notes)}개의 노트를 찾았습니다"
        )
        
    except ValueError as e:
        return controller.validation_error("tag", str(e))
    except Exception as e:
        return controller.error_response(
            message="태그별 노트 조회 실패",
            details=str(e),
            status=500
        )


@notes_bp.route('/notes/stats', methods=['GET'])
def get_stats():
    """노트 통계"""
    try:
        stats = controller.service.get_note_stats()
        
        return controller.success_response(
            data=stats,
            message="통계를 조회했습니다"
        )
        
    except Exception as e:
        return controller.error_response(
            message="통계 조회 실패",
            details=str(e),
            status=500
        )


# ====== 추가 유틸리티 엔드포인트 ======

@notes_bp.route('/notes/recent', methods=['GET'])
def get_recent_notes():
    """최근 노트들 (빠른 접근용)"""
    from flask import request
    
    limit = request.args.get('limit', 10, type=int)
    
    # 검색에서 query=None으로 호출하면 최근 노트를 반환
    from app.services.note_service import NoteService
    service = NoteService()
    notes = service.search_notes(limit=limit)
    
    response_data = {
        "notes": [controller._note_to_dict(note) for note in notes],
        "total": len(notes)
    }
    
    return controller.success_response(
        data=response_data,
        message=f"최근 {len(notes)}개의 노트를 조회했습니다"
    )


@notes_bp.route('/notes/validate', methods=['POST'])
def validate_note_data():
    """노트 데이터 검증 (프론트엔드용 유틸리티)"""
    data, error = controller.get_json_data()
    if error:
        return error
    
    try:
        # 검증만 수행 (실제 저장하지 않음)
        title = data.get('title', '')
        content = data.get('content', '')
        tags = data.get('tags', [])
        
        # 기본 검증
        validation_result = {
            "valid": True,
            "errors": [],
            "warnings": []
        }
        
        # 제목 검증
        if not title or not title.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("제목은 필수입니다")
        elif len(title.strip()) > 200:
            validation_result["valid"] = False
            validation_result["errors"].append("제목은 200자를 초과할 수 없습니다")
        
        # 내용 검증
        if not content or not content.strip():
            validation_result["valid"] = False
            validation_result["errors"].append("내용은 필수입니다")
        
        # 태그 검증
        from app.services.note_service import NoteService
        service = NoteService()
        
        if tags:
            validated_tags = service.validate_tags(tags)
            if len(validated_tags) != len(tags):
                validation_result["warnings"].append("일부 태그가 정리되었습니다")
        
        # 자동 추출된 태그 정보 제공
        if content:
            auto_tags = service.extract_tags_from_content(content)
            validation_result["auto_tags"] = auto_tags
        
        return controller.success_response(
            data=validation_result,
            message="검증이 완료되었습니다"
        )
        
    except Exception as e:
        return controller.error_response(
            message="검증 중 오류가 발생했습니다",
            details=str(e),
            status=500
        )