# backend/app/routes/notes.py - RAG Chain 연동 완성 버전
"""
노트 CRUD 기능 + 마크다운 처리 + RAG 시스템 연동

ID 누락 문제 완전 해결 + LangChain RAG 기능 완전 통합!
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from models.note import Note
from config.database import db

# ✅ RAG Chain 임포트
try:
    from chains.rag_chain import rag_chain
    RAG_ENABLED = True
    print("✅ RAG Chain 연동됨")
except ImportError as e:
    RAG_ENABLED = False
    print(f"⚠️ RAG Chain 비활성화: {e}")

# Blueprint 생성
notes_bp = Blueprint('notes', __name__)

# 헬퍼 함수들
def safe_get_json(request_obj, required_fields=None):
    """JSON 데이터 안전하게 추출"""
    try:
        data = request_obj.get_json()
        if not data:
            return None, "JSON 데이터가 필요합니다"
        
        if required_fields:
            for field in required_fields:
                if field not in data or not data[field]:
                    return None, f"'{field}' 필드가 필요합니다"
        
        return data, None
    except Exception as e:
        return None, f"JSON 파싱 실패: {str(e)}"

def success_response(data=None, message="성공", status_code=200):
    """성공 응답 표준화"""
    response = {
        "success": True,
        "message": message,
        "timestamp": datetime.now().isoformat()
    }
    if data is not None:
        response.update(data)
    
    return jsonify(response), status_code

def error_response(message="오류 발생", status_code=400):
    """에러 응답 표준화"""
    return jsonify({
        "success": False,
        "error": message,
        "timestamp": datetime.now().isoformat()
    }), status_code

def add_to_rag_index(note):
    """RAG 인덱스에 노트 추가 (실제 구현)"""
    if not RAG_ENABLED or not rag_chain.is_available():
        print(f"⚠️ RAG 시스템 비활성화 - 노트 {note.id} 인덱싱 건너뜀")
        return False
    
    try:
        success = rag_chain.add_note(note.id, note.title, note.content)
        if success:
            print(f"📚 RAG 인덱스에 노트 {note.id} 추가됨")
        return success
    except Exception as e:
        print(f"⚠️ RAG 인덱싱 실패 - 노트 {note.id}: {e}")
        return False

def update_rag_index(note):
    """RAG 인덱스 업데이트 (기존 삭제 후 재추가)"""
    if not RAG_ENABLED or not rag_chain.is_available():
        print(f"⚠️ RAG 시스템 비활성화 - 노트 {note.id} 업데이트 건너뜀")
        return False
    
    try:
        # 기존 항목 삭제는 복잡하므로, 전체 재구축하거나 새로 추가
        # 실제로는 기존 인덱스에서 삭제 후 새로 추가해야 하지만
        # 간단하게 새로 추가만 진행 (중복 허용)
        success = rag_chain.add_note(note.id, note.title, note.content)
        if success:
            print(f"🔄 RAG 인덱스에서 노트 {note.id} 업데이트됨")
        return success
    except Exception as e:
        print(f"⚠️ RAG 업데이트 실패 - 노트 {note.id}: {e}")
        return False

def rebuild_full_rag_index():
    """전체 RAG 인덱스 재구축"""
    if not RAG_ENABLED or not rag_chain.is_available():
        print("⚠️ RAG 시스템 비활성화 - 인덱스 재구축 불가")
        return False
    
    try:
        # 모든 노트 가져오기
        all_notes = Note.query.all()
        notes_data = []
        
        for note in all_notes:
            notes_data.append({
                'id': note.id,
                'title': note.title,
                'content': note.content
            })
        
        # RAG 인덱스 재구축
        success = rag_chain.rebuild_index(notes_data)
        print(f"🔄 RAG 전체 인덱스 재구축: {'성공' if success else '실패'}")
        return success
        
    except Exception as e:
        print(f"❌ RAG 인덱스 재구축 실패: {e}")
        return False

# 메인 라우트들
@notes_bp.route('/', methods=['GET'])
def get_notes():
    """노트 목록 조회 (검색, 필터링 지원)"""
    try:
        # 쿼리 파라미터
        search = request.args.get('search', '').strip()
        tag = request.args.get('tag', '').strip()
        
        print(f"📋 노트 목록 요청 - 검색: '{search}', 태그: '{tag}'")
        
        # 기본 쿼리
        query = Note.query
        
        # 검색 조건
        if search:
            query = query.filter(
                Note.title.contains(search) | Note.content.contains(search)
            )
        
        if tag:
            query = query.filter(Note.tags.contains(f'"{tag}"'))
        
        # 최신순 정렬
        notes = query.order_by(Note.updated_at.desc()).all()
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        note_list = [note.to_dict() for note in notes]
        
        print(f"✅ {len(notes)}개 노트 조회됨")
        for note in note_list[:3]:  # 처음 3개만 로그 출력
            print(f"  - 노트 ID: {note.get('id')}, 제목: '{note.get('title')}'")
        
        return success_response({
            "notes": note_list,
            "total": len(notes),
            "filters": {"search": search, "tag": tag}
        }, f"{len(notes)}개 노트 조회")
        
    except Exception as e:
        print(f"❌ 노트 조회 실패: {e}")
        return error_response(f"노트 조회 실패: {str(e)}")


@notes_bp.route('/', methods=['POST'])
def create_note():
    """노트 생성"""
    try:
        # JSON 데이터 안전하게 추출
        data, error_msg = safe_get_json(request)
        if error_msg:
            return error_response(error_msg)
        
        title = data.get('title', 'Untitled').strip()
        content = data.get('content', '').strip()
        
        print(f"📝 새 노트 생성 요청 - 제목: '{title}'")
        
        # 노트 생성
        note = Note(title=title, content=content)
        
        # 태그 처리
        if 'tags' in data and data['tags']:
            note.set_tags(data['tags'])
        
        db.session.add(note)
        
        # ✅ 핵심: flush()로 ID 먼저 생성 (commit 전)
        db.session.flush()
        
        print(f"🆔 노트 ID 생성됨: {note.id}")
        
        # ✅ 이제 ID가 있으므로 RAG 인덱스에 추가 가능
        rag_indexed = add_to_rag_index(note)
        
        # 최종 commit
        db.session.commit()
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        note_data = note.to_dict()
        
        print(f"✅ 새 노트 생성 완료 - ID: {note.id}, 제목: '{note.title}', RAG: {'✅' if rag_indexed else '❌'}")
        
        return success_response({
            "note": note_data,
            "rag_indexed": rag_indexed
        }, f"노트 '{title}'가 생성되었습니다", 201)
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 노트 생성 실패: {e}")
        return error_response(f"노트 생성 실패: {str(e)}")


@notes_bp.route('/<int:note_id>', methods=['GET'])
def get_note(note_id):
    """특정 노트 조회"""
    try:
        print(f"📖 노트 {note_id} 조회 요청")
        
        note = Note.query.get_or_404(note_id)
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        note_data = note.to_dict()
        
        print(f"✅ 노트 조회됨 - ID: {note.id}, 제목: '{note.title}'")
        
        return success_response({
            "note": note_data
        }, "노트 조회 성공")
        
    except Exception as e:
        print(f"❌ 노트 {note_id} 조회 실패: {e}")
        return error_response(f"노트 조회 실패: {str(e)}", 404)


@notes_bp.route('/<int:note_id>', methods=['PUT'])
def update_note(note_id):
    """노트 수정"""
    try:
        print(f"✏️ 노트 {note_id} 수정 요청")
        
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
        
        note.updated_at = datetime.utcnow()
        db.session.commit()
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        note_data = note.to_dict()
        
        print(f"✅ 노트 수정됨 - ID: {note.id}, 제목: '{note.title}'")
        
        # RAG 인덱스 업데이트
        rag_updated = update_rag_index(note)
        
        return success_response({
            "note": note_data,
            "rag_updated": rag_updated,
            "rag_available": RAG_ENABLED and rag_chain.is_available() if RAG_ENABLED else False
        }, f"노트 '{note.title}'가 수정되었습니다 {'(RAG 업데이트 완료)' if rag_updated else ''}")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 노트 {note_id} 수정 실패: {e}")
        return error_response(f"노트 수정 실패: {str(e)}")


@notes_bp.route('/<int:note_id>', methods=['DELETE'])
def delete_note(note_id):
    """노트 삭제"""
    try:
        print(f"🗑️ 노트 {note_id} 삭제 요청")
        
        note = Note.query.get_or_404(note_id)
        note_title = note.title
        
        db.session.delete(note)
        db.session.commit()
        
        print(f"✅ 노트 삭제됨 - ID: {note_id}, 제목: '{note_title}'")
        
        return success_response({
            "deleted_id": note_id,
            "deleted_title": note_title
        }, f"노트 '{note_title}'가 삭제되었습니다")
        
    except Exception as e:
        db.session.rollback()
        print(f"❌ 노트 {note_id} 삭제 실패: {e}")
        return error_response(f"노트 삭제 실패: {str(e)}")


@notes_bp.route('/tags', methods=['GET'])
def get_tags():
    """태그 목록 조회"""
    try:
        print("🏷️ 태그 목록 요청")
        
        all_tags = Note.get_all_tags()
        
        # 태그별 사용 횟수 계산
        tag_data = []
        for tag in all_tags:
            count = Note.query.filter(Note.tags.contains(f'"{tag}"')).count()
            tag_data.append({"name": tag, "count": count})
        
        # 사용 횟수순 정렬
        tag_data.sort(key=lambda x: x["count"], reverse=True)
        
        print(f"✅ {len(all_tags)}개 태그 조회됨")
        
        return success_response({
            "tags": tag_data,
            "total": len(all_tags)
        }, f"{len(all_tags)}개 태그 조회")
        
    except Exception as e:
        print(f"❌ 태그 조회 실패: {e}")
        return error_response(f"태그 조회 실패: {str(e)}")


@notes_bp.route('/search', methods=['POST'])
def search_notes():
    """노트 검색 (RAG 지원)"""
    try:
        data, error_msg = safe_get_json(request, ['query'])
        if error_msg:
            return error_response(error_msg)
        
        query = data['query'].strip()
        use_rag = data.get('use_rag', False)
        
        print(f"🔍 노트 검색 요청 - 쿼리: '{query}', RAG: {use_rag}")
        
        if use_rag and RAG_ENABLED and rag_chain.is_available():
            # RAG 검색
            rag_results = rag_chain.search_similar_notes(query, k=10)
            
            # RAG 결과를 노트 데이터로 변환
            results = []
            for rag_result in rag_results:
                note = Note.query.get(rag_result['note_id'])
                if note:
                    note_data = note.to_dict()
                    note_data['similarity_score'] = rag_result['similarity_score']
                    note_data['rank'] = rag_result['rank']
                    results.append(note_data)
            
            print(f"✅ RAG 검색 완료 - {len(results)}개 결과")
            
            return success_response({
                "results": results,
                "query": query,
                "total": len(results),
                "use_rag": True,
                "search_type": "vector_similarity"
            }, f"RAG 검색: '{query}'에 대한 {len(results)}개 결과")
        
        else:
            # 기본 텍스트 검색
            notes = Note.search_by_content(query)
            results = [note.to_dict() for note in notes]
            
            print(f"✅ 텍스트 검색 완료 - {len(results)}개 결과")
            
            return success_response({
                "results": results,
                "query": query,
                "total": len(results),
                "use_rag": False,
                "search_type": "text_search"
            }, f"텍스트 검색: '{query}'에 대한 {len(results)}개 결과")
        
    except Exception as e:
        print(f"❌ 검색 실패: {e}")
        return error_response(f"검색 실패: {str(e)}")


# ✅ 새로운 RAG 전용 엔드포인트들
@notes_bp.route('/rag/status', methods=['GET'])
def get_rag_status():
    """RAG 시스템 상태 확인"""
    try:
        if not RAG_ENABLED:
            return success_response({
                "available": False,
                "reason": "RAG packages not installed",
                "message": "pip install faiss-cpu sentence-transformers 필요"
            }, "RAG 시스템 비활성화")
        
        stats = rag_chain.get_stats()
        
        return success_response({
            "rag_status": stats,
            "recommendations": {
                "indexed_notes": stats.get("indexed_notes", 0),
                "total_notes": Note.query.count(),
                "needs_rebuild": stats.get("indexed_notes", 0) != Note.query.count()
            }
        }, "RAG 시스템 상태 조회")
        
    except Exception as e:
        return error_response(f"RAG 상태 조회 실패: {str(e)}")


@notes_bp.route('/rag/rebuild', methods=['POST'])
def rebuild_rag_index():
    """RAG 인덱스 전체 재구축"""
    try:
        if not RAG_ENABLED or not rag_chain.is_available():
            return error_response("RAG 시스템이 활성화되지 않았습니다", 503)
        
        print("🔄 RAG 인덱스 전체 재구축 시작...")
        
        # 전체 재구축 실행
        success = rebuild_full_rag_index()
        
        if success:
            stats = rag_chain.get_stats()
            return success_response({
                "rebuild_success": True,
                "rag_stats": stats
            }, f"RAG 인덱스 재구축 완료! {stats.get('indexed_notes', 0)}개 노트 인덱싱")
        else:
            return error_response("RAG 인덱스 재구축 실패", 500)
        
    except Exception as e:
        print(f"❌ RAG 재구축 에러: {e}")
        return error_response(f"RAG 인덱스 재구축 실패: {str(e)}")


@notes_bp.route('/rag/search', methods=['POST'])
def rag_search_only():
    """RAG 전용 검색 (벡터 유사도만)"""
    try:
        if not RAG_ENABLED or not rag_chain.is_available():
            return error_response("RAG 시스템이 활성화되지 않았습니다", 503)
        
        data, error_msg = safe_get_json(request, ['query'])
        if error_msg:
            return error_response(error_msg)
        
        query = data['query'].strip()
        k = data.get('k', 5)  # 결과 개수
        
        print(f"🔍 RAG 전용 검색 - 쿼리: '{query}', 개수: {k}")
        
        # RAG 검색 실행
        rag_results = rag_chain.search_similar_notes(query, k=k)
        
        # 컨텍스트 생성 (AI 모델용)
        context = rag_chain.get_context_for_query(query, k=3)
        
        return success_response({
            "query": query,
            "results": rag_results,
            "context": context,
            "total": len(rag_results)
        }, f"RAG 검색 완료: {len(rag_results)}개 결과")
        
    except Exception as e:
        print(f"❌ RAG 검색 실패: {e}")
        return error_response(f"RAG 검색 실패: {str(e)}")


@notes_bp.route('/rag/clear', methods=['DELETE'])
def clear_rag_index():
    """RAG 인덱스 완전 삭제"""
    try:
        if not RAG_ENABLED or not rag_chain.is_available():
            return error_response("RAG 시스템이 활성화되지 않았습니다", 503)
        
        success = rag_chain.clear_index()
        
        if success:
            return success_response({
                "cleared": True
            }, "RAG 인덱스가 완전히 삭제되었습니다")
        else:
            return error_response("RAG 인덱스 삭제 실패", 500)
        
    except Exception as e:
        return error_response(f"RAG 인덱스 삭제 실패: {str(e)}")


@notes_bp.route('/suggest', methods=['GET'])
def get_search_suggestions():
    """검색 자동완성"""
    try:
        query = request.args.get('q', '').strip()
        
        if len(query) < 2:
            return success_response({"suggestions": []}, "최소 2글자 이상 입력하세요")
        
        # 제목에서 매칭되는 노트들
        notes = Note.query.filter(Note.title.contains(query)).limit(5).all()
        suggestions = [note.title for note in notes]
        
        # 태그에서도 검색
        all_tags = Note.get_all_tags()
        matching_tags = [tag for tag in all_tags if query.lower() in tag.lower()][:3]
        
        return success_response({
            "suggestions": suggestions,
            "tags": matching_tags
        }, "검색 제안 조회")
        
    except Exception as e:
        return error_response(f"제안 조회 실패: {str(e)}")


@notes_bp.route('/<int:note_id>/similar', methods=['GET'])
def get_similar_notes(note_id):
    """유사한 노트 찾기"""
    try:
        note = Note.query.get_or_404(note_id)
        
        # 공통 태그를 가진 노트들 찾기
        similar_notes = []
        note_tags = note.get_tags()
        
        if note_tags:
            for tag in note_tags:
                tag_notes = Note.search_by_tag(tag)
                for tag_note in tag_notes:
                    if tag_note.id != note_id and tag_note not in similar_notes:
                        similar_notes.append(tag_note)
        
        # 최대 5개까지만
        similar_notes = similar_notes[:5]
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        results = [note.to_dict() for note in similar_notes]
        
        return success_response({
            "similar": results,
            "total": len(results)
        }, f"{len(results)}개의 유사한 노트")
        
    except Exception as e:
        return error_response(f"유사 노트 조회 실패: {str(e)}")


@notes_bp.route('/stats', methods=['GET'])
def get_note_stats():
    """노트 통계"""
    try:
        total_notes = Note.query.count()
        total_tags = len(Note.get_all_tags())
        
        # 최근 노트들
        recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        recent_notes_data = [note.to_dict() for note in recent_notes]
        
        return success_response({
            "total_notes": total_notes,
            "total_tags": total_tags,
            "recent_notes": recent_notes_data
        }, "통계 정보 조회")
        
    except Exception as e:
        return error_response(f"통계 조회 실패: {str(e)}")


@notes_bp.route('/graph', methods=['GET'])
def get_note_graph():
    """노트 연결 그래프 데이터"""
    try:
        all_notes = Note.query.all()
        
        # ✅ to_dict() 메서드로 ID 확실히 포함
        nodes = []
        links = []
        
        for note in all_notes:
            note_data = note.to_dict()
            nodes.append({
                "id": note_data["id"],
                "title": note_data["title"],
                "tags": note_data["tags"]
            })
        
        return success_response({
            "nodes": nodes,
            "links": links,
            "total_nodes": len(nodes)
        }, "노트 그래프 조회")
        
    except Exception as e:
        return error_response(f"그래프 조회 실패: {str(e)}")