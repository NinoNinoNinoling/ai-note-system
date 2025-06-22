# backend/app/routes/chat.py
from flask import Blueprint, request, jsonify
from datetime import datetime
from models.note import ChatHistory, db
from chains.rag_chain import rag_chain
from config.settings import Config

# Blueprint 생성
chat_bp = Blueprint('chat', __name__)

def get_claude_response(message: str, context: str = "") -> dict:
    """Claude API 호출 (실제 구현)"""
    try:
        if not Config.ANTHROPIC_API_KEY:
            raise Exception("Claude API 키가 설정되지 않았습니다")
        
        from langchain_anthropic import ChatAnthropic
        
        claude = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=Config.ANTHROPIC_API_KEY
        )
        
        # 컨텍스트가 있으면 프롬프트에 포함
        if context:
            full_prompt = f"""다음은 사용자의 노트들에서 찾은 관련 정보입니다:

{context}

위의 정보를 참고해서 다음 질문에 답해주세요:
{message}"""
        else:
            full_prompt = message
        
        response = claude.invoke(full_prompt)
        
        return {
            "response": response.content,
            "model": "Claude 3.5 Sonnet",
            "success": True
        }
        
    except Exception as e:
        return {
            "response": f"죄송합니다. AI 서비스에 일시적인 문제가 있습니다: {str(e)}",
            "model": "Error Fallback",
            "success": False,
            "error": str(e)
        }

def get_mock_response(message: str, context: str = "") -> dict:
    """Mock AI 응답 (개발/테스트용)"""
    mock_responses = {
        "요약": "주요 내용을 간단히 정리하면 다음과 같습니다...",
        "설명": "이 내용을 더 자세히 설명드리겠습니다...",
        "개선": "다음과 같이 개선해보시는 것은 어떨까요...",
        "질문": "좋은 질문이네요! 답변드리면...",
        "도움": "기꺼이 도와드리겠습니다!"
    }
    
    # 키워드 기반 응답 선택
    response_text = f"안녕하세요! '{message}'에 대해 도움을 드리겠습니다."
    
    for keyword, template in mock_responses.items():
        if keyword in message:
            response_text = template
            break
    
    # 컨텍스트가 있으면 추가
    if context:
        response_text += f"\n\n[관련 노트 정보]\n{context[:300]}..."
    
    response_text += "\n\n(현재는 Mock AI 응답입니다. Claude API 크레딧 충전 후 실제 답변으로 교체됩니다.)"
    
    return {
        "response": response_text,
        "model": "Mock AI (개발용)",
        "success": True
    }

@chat_bp.route('/test', methods=['GET'])
def test_claude():
    """Claude API 연결 테스트"""
    try:
        if not Config.ANTHROPIC_API_KEY:
            return jsonify({
                "status": "❌ API 키가 없습니다",
                "error": "ANTHROPIC_API_KEY를 .env 파일에 설정해주세요"
            }), 400
        
        result = get_claude_response("안녕하세요! API 테스트입니다.")
        
        if result["success"]:
            return jsonify({
                "status": "✅ Claude API 연결 성공!",
                "response": result["response"],
                "model": result["model"]
            })
        else:
            return jsonify({
                "status": "❌ Claude API 오류",
                "error": result["error"]
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "❌ 테스트 실패",
            "error": str(e)
        }), 500

@chat_bp.route('/', methods=['POST'])
def chat():
    """기본 AI 채팅 (컨텍스트 없음)"""
    try:
        data = request.get_json()
        message = data.get('message', '') if data else ''
        use_mock = data.get('use_mock', False) if data else False
        
        if not message:
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        # AI 응답 생성
        if use_mock or not Config.ANTHROPIC_API_KEY:
            result = get_mock_response(message)
        else:
            result = get_claude_response(message)
        
        # 채팅 기록 저장
        chat_record = ChatHistory(
            user_message=message,
            ai_response=result["response"],
            model_used=result["model"]
        )
        db.session.add(chat_record)
        db.session.commit()
        
        return jsonify({
            "user_message": message,
            "ai_response": result["response"],
            "model": result["model"],
            "chat_id": chat_record.id,
            "timestamp": datetime.utcnow().isoformat(),
            "success": result["success"]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"채팅 오류: {str(e)}"}), 500

@chat_bp.route('/rag', methods=['POST'])
def chat_with_rag():
    """RAG 기반 AI 채팅 (노트 컨텍스트 포함)"""
    try:
        data = request.get_json()
        message = data.get('message', '') if data else ''
        use_mock = data.get('use_mock', True) if data else True  # 기본값 True
        
        if not message:
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        # RAG로 관련 노트 검색
        context = ""
        related_notes = []
        
        if rag_chain.is_available():
            context = rag_chain.get_context_for_query(message, k=3)
            related_notes = rag_chain.search_similar_notes(message, k=3)
        
        # AI 응답 생성 (컨텍스트 포함)
        if use_mock or not Config.ANTHROPIC_API_KEY:
            result = get_mock_response(message, context)
        else:
            result = get_claude_response(message, context)
        
        # 채팅 기록 저장
        chat_record = ChatHistory(
            user_message=message,
            ai_response=result["response"],
            model_used=f"RAG + {result['model']}"
        )
        db.session.add(chat_record)
        db.session.commit()
        
        return jsonify({
            "user_message": message,
            "ai_response": result["response"],
            "model": result["model"],
            "chat_id": chat_record.id,
            "context_used": bool(context),
            "related_notes": related_notes,
            "rag_available": rag_chain.is_available(),
            "timestamp": datetime.utcnow().isoformat(),
            "success": result["success"]
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"RAG 채팅 오류: {str(e)}"}), 500

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """채팅 기록 조회"""
    try:
        note_id = request.args.get('note_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        
        chats = ChatHistory.get_recent_chats(note_id=note_id, limit=limit)
        
        return jsonify({
            "chats": [chat.to_dict() for chat in chats],
            "count": len(chats),
            "note_id": note_id,
            "limit": limit
        })
        
    except Exception as e:
        return jsonify({"error": f"채팅 기록 조회 오류: {str(e)}"}), 500

@chat_bp.route('/history/<int:chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """특정 채팅 기록 삭제"""
    try:
        chat = ChatHistory.query.get_or_404(chat_id)
        
        chat_info = chat.to_dict()
        
        db.session.delete(chat)
        db.session.commit()
        
        return jsonify({
            "message": "채팅 기록이 삭제되었습니다",
            "deleted_chat": chat_info
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"채팅 삭제 오류: {str(e)}"}), 500

@chat_bp.route('/history/clear', methods=['DELETE'])
def clear_chat_history():
    """모든 채팅 기록 삭제"""
    try:
        note_id = request.args.get('note_id', type=int)
        
        if note_id:
            # 특정 노트의 채팅만 삭제
            deleted_count = ChatHistory.query.filter_by(note_id=note_id).delete()
        else:
            # 모든 채팅 삭제
            deleted_count = ChatHistory.query.delete()
        
        db.session.commit()
        
        return jsonify({
            "message": f"{deleted_count}개의 채팅 기록이 삭제되었습니다",
            "deleted_count": deleted_count,
            "note_id": note_id
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"채팅 기록 삭제 오류: {str(e)}"}), 500

@chat_bp.route('/rag/rebuild', methods=['POST'])
def rebuild_rag_index():
    """RAG 인덱스 재구축"""
    try:
        if not rag_chain.is_available():
            return jsonify({"error": "RAG 시스템을 사용할 수 없습니다"}), 503
        
        from models.note import Note
        
        # 모든 노트 가져오기
        notes = Note.query.all()
        note_data = [{
            'id': note.id,
            'title': note.title,
            'content': note.content
        } for note in notes]
        
        # 인덱스 재구축
        success = rag_chain.rebuild_index(note_data)
        
        if success:
            return jsonify({
                "status": "✅ RAG 인덱스 재구축 완료",
                "indexed_notes": len(note_data),
                "rag_stats": rag_chain.get_stats()
            })
        else:
            return jsonify({"error": "RAG 인덱스 재구축 실패"}), 500
            
    except Exception as e:
        return jsonify({"error": f"인덱스 재구축 오류: {str(e)}"}), 500