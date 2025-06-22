# backend/app/routes/notes.py
from flask import Blueprint, request, jsonify
from models.note import Note, db
from chains.rag_chain import rag_chain

# Blueprint 생성
notes_bp = Blueprint('notes', __name__)

@notes_bp.route('/', methods=['GET'])
def get_notes():
    """모든 노트 조회"""
    try:
        # 쿼리 파라미터 처리
        search = request.args.get('search', '')
        tag = request.args.get('tag', '')
        limit = request.args.get('limit', type=int)
        
        # 기본 쿼리
        query = Note.query
        
        # 검색 조건 추가
        if search:
            query = query.filter(
                Note.title.contains(search) | Note.content.contains(search)
            )
        
        if tag:
            query = query.filter(Note.tags.contains(f'"{tag}"'))
        
        # 정렬 및 제한
        query = query.order_by(Note.updated_at.desc())
        if limit:
            query = query.limit(limit)
        
        notes = query.all()
        
        return jsonify({
            "notes": [note.to_dict() for note in notes],
            "count": len(notes),
            "filters": {
                "search": search,
                "tag": tag,
                "limit": limit
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"노트 조회 오류: {str(e)}"}), 500

@notes_bp.route('/', methods=['POST'])
def create_note():
    """새 노트 생성"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400
        
        # 노트 생성
        note = Note(
            title=data.get('title', '제목 없음'),
            content=data.get('content', '')
        )
        
        # 태그 설정
        if 'tags' in data:
            note.set_tags(data['tags'])
        
        # DB 저장
        db.session.add(note)
        db.session.commit()
        
        # RAG 시스템에 추가
        rag_indexed = False
        if rag_chain.is_available():
            rag_indexed = rag_chain.add_note(note.id, note.title, note.content)
        
        return jsonify({
            **note.to_dict(),
            "rag_indexed": rag_indexed,
            "message": "노트가 성공적으로 생성되었습니다"
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"노트 생성 오류: {str(e)}"}), 500

@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """특정 노트 조회"""
    try:
        note = Note.query.get_or_404(note_id)
        return jsonify(note.to_dict())
        
    except Exception as e:
        return jsonify({"error": f"노트 조회 오류: {str(e)}"}), 500

@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """노트 수정"""
    try:
        note = Note.query.get_or_404(note_id)
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "JSON 데이터가 필요합니다"}), 400
        
        # 데이터 업데이트
        if 'title' in data:
            note.title = data['title']
        if 'content' in data:
            note.content = data['content']
        if 'tags' in data:
            note.set_tags(data['tags'])
        
        # DB 저장
        db.session.commit()
        
        # RAG 인덱스 업데이트 (간단히 재추가)
        rag_updated = False
        if rag_chain.is_available():
            rag_updated = rag_chain.add_note(note.id, note.title, note.content)
        
        return jsonify({
            **note.to_dict(),
            "rag_updated": rag_updated,
            "message": "노트가 성공적으로 수정되었습니다"
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"노트 수정 오류: {str(e)}"}), 500

@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """노트 삭제"""
    try:
        note = Note.query.get_or_404(note_id)
        
        # 노트 정보 백업 (응답용)
        note_info = note.to_dict()
        
        # DB에서 삭제
        db.session.delete(note)
        db.session.commit()
        
        # TODO: RAG 인덱스에서도 제거 (현재는 전체 재구축 필요)
        
        return jsonify({
            "message": "노트가 성공적으로 삭제되었습니다",
            "deleted_note": note_info
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"노트 삭제 오류: {str(e)}"}), 500

@notes_bp.route('/tags', methods=['GET'])
def get_all_tags():
    """모든 태그 목록 조회"""
    try:
        tags = Note.get_all_tags()
        return jsonify({
            "tags": tags,
            "count": len(tags)
        })
        
    except Exception as e:
        return jsonify({"error": f"태그 조회 오류: {str(e)}"}), 500

@notes_bp.route('/search', methods=['POST'])
def search_notes():
    """노트 검색 (POST 방식)"""
    try:
        data = request.get_json()
        query = data.get('query', '') if data else ''
        
        if not query:
            return jsonify({"error": "검색어를 입력해주세요"}), 400
        
        # 텍스트 기반 검색
        text_results = Note.search_by_content(query)
        
        # RAG 기반 유사도 검색
        rag_results = []
        if rag_chain.is_available():
            rag_results = rag_chain.search_similar_notes(query, k=5)
        
        return jsonify({
            "query": query,
            "text_search": {
                "results": [note.to_dict() for note in text_results],
                "count": len(text_results)
            },
            "rag_search": {
                "results": rag_results,
                "count": len(rag_results),
                "available": rag_chain.is_available()
            }
        })
        
    except Exception as e:
        return jsonify({"error": f"검색 오류: {str(e)}"}), 500

@notes_bp.route('/stats', methods=['GET'])
def get_notes_stats():
    """노트 통계 정보"""
    try:
        total_notes = Note.query.count()
        recent_notes = Note.get_recent_notes(5)
        all_tags = Note.get_all_tags()
        
        return jsonify({
            "total_notes": total_notes,
            "total_tags": len(all_tags),
            "recent_notes": [note.to_dict() for note in recent_notes],
            "popular_tags": all_tags[:10],  # 상위 10개 태그
            "rag_stats": rag_chain.get_stats()
        })
        
    except Exception as e:
        return jsonify({"error": f"통계 조회 오류: {str(e)}"}), 500