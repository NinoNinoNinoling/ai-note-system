# backend/app/routes/notes.py - 개선된 노트 라우트
"""
노트 CRUD 기능 + 마크다운 처리

실용적인 기능들이 포함된 버전
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from models.note import Note
from config.database import db
from utils.response_utils import success_response, error_response, safe_get_json, format_note_response
from utils.search_utils import quick_search, advanced_search, note_searcher
from utils.markdown_utils import process_markdown_content, note_linker

# Blueprint 생성
notes_bp = Blueprint('notes', __name__)


@notes_bp.route('/', methods=['GET'])
def get_notes():
    """노트 목록 조회 (검색, 필터링 지원)"""
    try:
        # 쿼리 파라미터
        search = request.args.get('search', '').strip()
        tag = request.args.get('tag', '').strip()
        include_processed = request.args.get('processed', 'false').lower() == 'true'
        
        # 기본 쿼리
        query = Note.query
        
        # 검색 조건
        if search:
            # 검색 유틸 사용
            results = quick_search(search, limit=50)
            return success_response(
                data={
                    "notes": results,
                    "total": len(results),
                    "search_query": search,
                    "is_search_result": True
                },
                message=f"'{search}'에 대한 {len(results)}개 결과"
            )
        
        if tag:
            query = query.filter(Note.tags.contains(f'"{tag}"'))
        
        # 최신순 정렬
        notes = query.order_by(Note.updated_at.desc()).all()
        
        # 응답 형식화
        note_list = []
        for note in notes:
            note_data = format_note_response(note, include_processed)
            note_list.append(note_data)
        
        return success_response(
            data={
                "notes": note_list,
                "total": len(notes),
                "filters": {"tag": tag},
                "is_search_result": False
            },
            message=f"{len(notes)}개 노트 조회"
        )
        
    except Exception as e:
        return error_response(f"노트 조회 실패: {str(e)}")


@notes_bp.route('/', methods=['POST'])
def create_note():
    """노트 생성 (마크다운 처리 포함)"""
    try:
        # JSON 데이터 안전하게 추출
        data, error_msg = safe_get_json(request, ['title'])
        if error_msg:
            return error_response(error_msg)
        
        title = data['title'].strip()
        content = data.get('content', '').strip()
        
        # 노트 생성
        note = Note(title=title, content=content)
        
        # 태그 처리
        if 'tags' in data and data['tags']:
            note.set_tags(data['tags'])
        else:
            # 마크다운에서 자동 태그 추출
            from utils.markdown_utils import markdown_processor
            extracted_tags = markdown_processor.extract_tags(content)
            if extracted_tags:
                note.set_tags(extracted_tags)
        
        db.session.add(note)
        db.session.commit()
        
        # 마크다운 처리 결과 포함
        response_data = format_note_response(note, include_processed=True)
        
        # RAG 시스템에 추가 (LangChain 기능)
        rag_indexed = add_to_rag_index(note)
        
        return success_response(
            data={
                **response_data,
                "rag_indexed": rag_indexed  # RAG 인덱싱 결과 포함
            },
            message=f"노트 '{title}'가 생성되었습니다 (RAG: {'✅' if rag_indexed else '❌'})",
            status_code=201
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"노트 생성 실패: {str(e)}")


@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """특정 노트 조회 (관련 정보 포함)"""
    try:
        note = Note.query.get_or_404(note_id)
        
        # 마크다운 처리
        response_data = format_note_response(note, include_processed=True)
        
        # 추가 정보
        all_notes = Note.query.all()
        note_data_list = [{"id": n.id, "title": n.title, "content": n.content} for n in all_notes]
        
        # 백링크 찾기
        backlinks = note_linker.find_backlinks(note.title, note_data_list)
        
        # 유사 노트 찾기
        similar_notes = note_searcher.find_similar_notes(note, limit=3)
        
        response_data.update({
            "backlinks": backlinks,
            "similar_notes": [{"id": n.id, "title": n.title} for n in similar_notes]
        })
        
        return success_response(
            data=response_data,
            message="노트 조회 성공"
        )
        
    except Exception as e:
        return error_response(f"노트 조회 실패: {str(e)}")


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """노트 수정 (마크다운 재처리)"""
    try:
        note = Note.query.get_or_404(note_id)
        
        data, error_msg = safe_get_json(request)
        if error_msg:
            return error_response(error_msg)
        
        # 데이터 업데이트
        if 'title' in data:
            title = data['title'].strip()
            if not title:
                return error_response("제목은 비어있을 수 없습니다")
            note.title = title
            
        if 'content' in data:
            note.content = data['content'].strip()
            
        if 'tags' in data:
            note.set_tags(data['tags'])
        
        note.updated_at = datetime.now()
        db.session.commit()
        
        # 마크다운 처리 결과 포함
        response_data = format_note_response(note, include_processed=True)
        
        # RAG 인덱스 업데이트 (LangChain 기능)
        rag_updated = update_rag_index(note)
        
        return success_response(
            data={
                **response_data,
                "rag_updated": rag_updated  # RAG 업데이트 결과 포함
            },
            message=f"노트 '{note.title}'가 수정되었습니다 (RAG: {'✅' if rag_updated else '❌'})"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"노트 수정 실패: {str(e)}")


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """노트 삭제"""
    try:
        note = Note.query.get_or_404(note_id)
        note_title = note.title
        
        db.session.delete(note)
        db.session.commit()
        
        return success_response(
            data={"deleted_id": note_id, "deleted_title": note_title},
            message=f"노트 '{note_title}'가 삭제되었습니다"
        )
        
    except Exception as e:
        db.session.rollback()
        return error_response(f"노트 삭제 실패: {str(e)}")


@notes_bp.route('/tags', methods=['GET'])
def get_tags():
    """태그 목록 조회 (사용 횟수 포함)"""
    try:
        all_tags = Note.get_all_tags()
        
        # 태그별 사용 횟수 계산
        tag_counts = {}
        for tag in all_tags:
            count = Note.query.filter(Note.tags.contains(f'"{tag}"')).count()
            tag_counts[tag] = count
        
        # 사용 횟수순 정렬
        sorted_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)
        
        return success_response(
            data={
                "tags": [{"name": tag, "count": count} for tag, count in sorted_tags],
                "total_tags": len(all_tags),
                "total_notes": Note.query.count()
            },
            message=f"{len(all_tags)}개 태그 조회"
        )
        
    except Exception as e:
        return error_response(f"태그 조회 실패: {str(e)}")


@notes_bp.route('/search', methods=['POST'])
def search_notes():
    """고급 노트 검색"""
    try:
        data, error_msg = safe_get_json(request, ['query'])
        if error_msg:
            return error_response(error_msg)
        
        query = data['query'].strip()
        tags = data.get('tags', [])
        date_from = data.get('date_from')
        date_to = data.get('date_to')
        
        # 고급 검색 실행
        results = advanced_search(query, tags, date_from, date_to)
        
        return success_response(
            data={
                "query": query,
                "results": results,
                "total": len(results),
                "filters": {
                    "tags": tags,
                    "date_from": date_from,
                    "date_to": date_to
                }
            },
            message=f"'{query}'에 대한 {len(results)}개 결과"
        )
        
    except Exception as e:
        return error_response(f"검색 실패: {str(e)}")


@notes_bp.route('/suggest', methods=['GET'])
def get_search_suggestions():
    """검색 자동완성 제안"""
    try:
        partial_query = request.args.get('q', '').strip()
        
        if len(partial_query) < 2:
            return success_response(
                data={"suggestions": []},
                message="최소 2글자 이상 입력하세요"
            )
        
        suggestions = note_searcher.get_search_suggestions(partial_query)
        
        return success_response(
            data={"suggestions": suggestions},
            message="검색 제안 조회"
        )
        
    except Exception as e:
        return error_response(f"제안 조회 실패: {str(e)}")


@notes_bp.route('/<int:note_id>/similar', methods=['GET'])
def get_similar_notes(note_id):
    """유사한 노트 찾기"""
    try:
        note = Note.query.get_or_404(note_id)
        
        similar_notes = note_searcher.find_similar_notes(note, limit=5)
        
        results = []
        for similar_note in similar_notes:
            results.append({
                "id": similar_note.id,
                "title": similar_note.title,
                "preview": process_markdown_content(similar_note.content)["preview"],
                "tags": similar_note.get_tags(),
                "updated_at": similar_note.updated_at.isoformat() if similar_note.updated_at else None
            })
        
        return success_response(
            data={"similar_notes": results},
            message=f"'{note.title}'와 유사한 {len(results)}개 노트"
        )
        
    except Exception as e:
        return error_response(f"유사 노트 조회 실패: {str(e)}")


@notes_bp.route('/graph', methods=['GET'])
def get_note_graph():
    """노트 연결 그래프 데이터"""
    try:
        all_notes = Note.query.all()
        note_data_list = [
            {
                "id": note.id,
                "title": note.title,
                "content": note.content,
                "tags": note.get_tags()
            }
            for note in all_notes
        ]
        
        graph_data = note_linker.create_note_graph(note_data_list)
        
        return success_response(
            data=graph_data,
            message="노트 연결 그래프 조회"
        )
        
    except Exception as e:
        return error_response(f"그래프 조회 실패: {str(e)}")


@notes_bp.route('/stats', methods=['GET'])
def get_note_stats():
    """노트 통계 정보"""
    try:
        total_notes = Note.query.count()
        total_tags = len(Note.get_all_tags())
        
        # 최근 노트들
        recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()
        
        # 가장 많이 사용된 태그들
        all_tags = Note.get_all_tags()
        popular_tags = []
        for tag in all_tags[:10]:  # 상위 10개
            count = Note.query.filter(Note.tags.contains(f'"{tag}"')).count()
            popular_tags.append({"name": tag, "count": count})
        
        popular_tags.sort(key=lambda x: x["count"], reverse=True)
        
        # 전체 단어 수
        total_chars = sum(len(note.content) for note in Note.query.all())
        
        return success_response(
            data={
                "total_notes": total_notes,
                "total_tags": total_tags,
                "total_characters": total_chars,
                "recent_notes": [format_note_response(note) for note in recent_notes],
                "popular_tags": popular_tags[:5]
            },
            message="통계 정보 조회"
        )
        
    except Exception as e:
        return error_response(f"통계 조회 실패: {str(e)}")