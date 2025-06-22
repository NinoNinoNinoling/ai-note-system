# backend/app.py
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

app = Flask(__name__)

# 환경변수에서 설정 읽기
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'fallback-secret-key')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///ai_notes.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# RAG 시스템 임포트
try:
    from rag_system import rag
    RAG_AVAILABLE = True
    print("✅ RAG 시스템 로드 완료")
except Exception as e:
    RAG_AVAILABLE = False
    print(f"⚠️ RAG 시스템 로드 실패: {e}")

# 노트 모델
class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# 기본 라우트
@app.route('/')
def index():
    note_count = Note.query.count()
    return jsonify({
        "message": "AI Note System with RAG", 
        "status": "running",
        "total_notes": note_count,
        "rag_available": RAG_AVAILABLE
    })

# 노트 관련 API
@app.route('/api/notes', methods=['GET'])
def get_notes():
    notes = Note.query.order_by(Note.created_at.desc()).all()
    return jsonify([{
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat()
    } for note in notes])

@app.route('/api/notes', methods=['POST'])
def create_note():
    data = request.get_json()
    
    note = Note(
        title=data.get('title', '제목 없음'),
        content=data.get('content', '')
    )
    
    db.session.add(note)
    db.session.commit()
    
    # RAG 시스템에 노트 추가
    if RAG_AVAILABLE:
        try:
            rag.add_note(note.id, note.title, note.content)
        except Exception as e:
            print(f"RAG 추가 오류: {e}")
    
    return jsonify({
        "id": note.id,
        "title": note.title,
        "content": note.content,
        "created_at": note.created_at.isoformat(),
        "rag_indexed": RAG_AVAILABLE
    }), 201

# RAG 검색 API
@app.route('/api/search', methods=['POST'])
def search_notes():
    if not RAG_AVAILABLE:
        return jsonify({"error": "RAG 시스템을 사용할 수 없습니다"}), 503
    
    data = request.get_json()
    query = data.get('query', '')
    
    if not query:
        return jsonify({"error": "검색어를 입력해주세요"}), 400
    
    try:
        # RAG로 유사한 노트 검색
        similar_notes = rag.search_similar_notes(query, k=5)
        
        return jsonify({
            "query": query,
            "results": similar_notes,
            "count": len(similar_notes)
        })
        
    except Exception as e:
        return jsonify({"error": f"검색 오류: {str(e)}"}), 500

# RAG + Claude 결합 API  
@app.route('/api/chat-rag', methods=['POST'])
def chat_with_rag():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        # RAG로 관련 노트 찾기
        context = ""
        if RAG_AVAILABLE:
            context = rag.get_context_for_query(message, k=3)
        
        # Mock AI 응답 (크레딧 문제로)
        ai_response = f"""
안녕하세요! '{message}'에 대해 답변드리겠습니다.

{context}

위의 노트들을 바탕으로 답변드리면:
[여기에 Claude의 실제 답변이 들어갈 예정입니다]

(현재는 Mock 응답입니다. Claude API 크레딧 충전 후 실제 AI 답변으로 교체됩니다.)
        """.strip()
        
        return jsonify({
            "user_message": message,
            "ai_response": ai_response,
            "context_used": context != "",
            "model": "RAG + Mock AI",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"RAG 채팅 오류: {str(e)}"}), 500

# RAG 인덱스 재구축 API
@app.route('/api/rebuild-index', methods=['POST'])
def rebuild_index():
    if not RAG_AVAILABLE:
        return jsonify({"error": "RAG 시스템을 사용할 수 없습니다"}), 503
    
    try:
        # 모든 노트 가져오기
        notes = Note.query.all()
        note_data = [{
            'id': note.id,
            'title': note.title,
            'content': note.content
        } for note in notes]
        
        # 인덱스 재구축
        rag.rebuild_index(note_data)
        
        return jsonify({
            "status": "✅ RAG 인덱스 재구축 완료",
            "indexed_notes": len(note_data)
        })
        
    except Exception as e:
        return jsonify({"error": f"인덱스 재구축 오류: {str(e)}"}), 500

# Claude AI 관련 API
@app.route('/test-claude')
def test_claude():
    try:
        from langchain_anthropic import ChatAnthropic
        
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            return jsonify({
                "status": "❌ API 키가 없습니다",
                "error": "ANTHROPIC_API_KEY를 .env 파일에 설정해주세요"
            }), 400
        
        claude = ChatAnthropic(
            model="claude-3-5-sonnet-20241022", 
            anthropic_api_key=api_key
        )
        
        response = claude.invoke("안녕하세요! API 테스트입니다.")
        
        return jsonify({
            "status": "✅ Claude API 연결 성공!",
            "response": response.content,
            "model": "Claude 3.5 Sonnet"
        })
        
    except Exception as e:
        return jsonify({
            "status": "❌ Claude API 오류",
            "error": str(e)
        }), 500

@app.route('/api/chat', methods=['POST'])
def chat_with_claude():
    try:
        data = request.get_json()
        message = data.get('message', '')
        
        if not message:
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        # 크레딧 부족 시 Mock 응답 사용
        api_key = os.getenv('ANTHROPIC_API_KEY')
        use_mock = not api_key  # API 키 없으면 Mock 사용
        
        if use_mock:
            # Mock AI 응답 (개발용)
            mock_responses = {
                "요약": f"'{message}'에 대한 요약: 주요 내용을 간단히 정리하면 다음과 같습니다.",
                "설명": f"'{message}'에 대한 설명: 이 내용을 더 자세히 설명드리겠습니다.",
                "개선": f"'{message}'에 대한 개선 제안: 다음과 같이 개선해보시는 것은 어떨까요?"
            }
            
            # 키워드 기반 응답 선택
            for key, response in mock_responses.items():
                if key in message:
                    ai_response = response
                    break
            else:
                ai_response = f"안녕하세요! '{message}'에 대해 도움을 드리겠습니다. (Mock AI 응답 - 개발용)"
            
            return jsonify({
                "user_message": message,
                "ai_response": ai_response,
                "model": "Mock AI (개발용)",
                "timestamp": datetime.utcnow().isoformat(),
                "note": "실제 Claude API는 크레딧 충전 후 사용 가능합니다."
            })
        
        # 실제 Claude API 사용
        from langchain_anthropic import ChatAnthropic
        
        claude = ChatAnthropic(
            model="claude-3-5-sonnet-20241022",
            anthropic_api_key=api_key
        )
        
        response = claude.invoke(message)
        
        return jsonify({
            "user_message": message,
            "ai_response": response.content,
            "model": "Claude 3.5 Sonnet",
            "timestamp": datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        # 크레딧 부족 등 API 오류 시 Mock 응답으로 폴백
        return jsonify({
            "user_message": message,
            "ai_response": f"죄송합니다. 현재 AI 서비스에 일시적인 문제가 있습니다. '{message}'에 대한 응답을 준비 중입니다. (임시 응답)",
            "model": "Fallback Mock AI",
            "timestamp": datetime.utcnow().isoformat(),
            "error_note": "Claude API 크레딧 부족 또는 연결 오류"
        })

# 테스트 관련 API
@app.route('/test-db')
def test_db():
    try:
        # DB 테이블 생성
        db.create_all()
        
        # 테스트 노트 생성
        test_note = Note(title="첫 번째 노트", content="DB 테스트입니다!")
        db.session.add(test_note)
        db.session.commit()
        
        return jsonify({
            "status": "✅ DB 테스트 성공!",
            "note_id": test_note.id,
            "note_count": Note.query.count()
        })
        
    except Exception as e:
        return jsonify({
            "status": "❌ DB 오류",
            "error": str(e)
        }), 500

if __name__ == '__main__':
    # DB 테이블 생성
    with app.app_context():
        db.create_all()
    
    print("🧠 AI Note System with RAG 시작!")
    print("📍 http://localhost:5000")
    print("🧪 테스트 URL:")
    print("   http://localhost:5000/test-db           - DB 테스트")
    print("   http://localhost:5000/test-claude       - Claude API 테스트") 
    print("   http://localhost:5000/api/notes         - 노트 목록")
    print("🔍 RAG 기능:")
    print("   POST /api/search                        - 노트 검색")
    print("   POST /api/chat-rag                      - RAG + AI 채팅")
    print("   POST /api/rebuild-index                 - 인덱스 재구축")
    
    app.run(debug=True)