# backend/app/routes/chat.py - 심플한 채팅 라우트
"""
AI 채팅 기능

과제용 심플 버전 - 안정성 우선!
"""

from flask import Blueprint, request, jsonify
from datetime import datetime
from config.settings import Config

# Blueprint 생성
chat_bp = Blueprint('chat', __name__)


def get_claude_response(message: str) -> dict:
    """Claude API 호출"""
    try:
        if not Config.ANTHROPIC_API_KEY:
            return {
                "response": "Claude API 키가 설정되지 않았습니다. .env 파일을 확인해주세요.",
                "model": "Error",
                "success": False
            }
        
        from anthropic import Anthropic
        
        client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1000,
            messages=[
                {"role": "user", "content": message}
            ]
        )
        
        return {
            "response": response.content[0].text,
            "model": "Claude 3.5 Sonnet",
            "success": True
        }
        
    except Exception as e:
        return {
            "response": f"Claude API 오류: {str(e)}\n\nMock 모드로 전환합니다.",
            "model": "Error → Mock",
            "success": False
        }


def get_mock_response(message: str) -> dict:
    """Mock AI 응답"""
    
    # 키워드 기반 응답
    message_lower = message.lower()
    
    if any(word in message_lower for word in ['안녕', 'hello', '헬로', '반가']):
        response = "안녕하세요! AI Note System의 AI 어시스턴트입니다. 무엇을 도와드릴까요?"
        
    elif any(word in message_lower for word in ['마크다운', 'markdown']):
        response = """마크다운(Markdown)은 간단한 문법으로 텍스트를 포맷팅할 수 있는 언어입니다.

**주요 문법:**
- `# 제목 1`, `## 제목 2` - 헤더
- `**굵은글씨**`, `*기울임*` - 텍스트 스타일  
- `- 항목` - 리스트
- `` `코드` `` - 인라인 코드
- `[링크](URL)` - 링크

노트 시스템에서 마크다운을 사용해 멋진 노트를 작성해보세요! 📝"""

    elif any(word in message_lower for word in ['vue', 'vuejs', '뷰']):
        response = """Vue.js는 사용자 인터페이스를 구축하기 위한 JavaScript 프레임워크입니다.

**주요 특징:**
- 📦 **컴포넌트 기반** - 재사용 가능한 UI 컴포넌트
- 🔄 **반응형 데이터** - 데이터 변경시 자동 UI 업데이트
- 🎯 **단순함** - 학습하기 쉬운 문법
- ⚡ **성능** - 가상 DOM으로 빠른 렌더링

Composition API를 사용하면 더 깔끔한 코드를 작성할 수 있어요!"""

    elif any(word in message_lower for word in ['python', 'flask', '파이썬', '플라스크']):
        response = """Python과 Flask로 웹 개발을 하고 계시는군요! 

**Flask의 장점:**
- 🚀 **경량성** - 최소한의 구성으로 시작
- 🔧 **유연성** - 원하는 라이브러리 자유롭게 선택
- 📚 **간단함** - 배우기 쉬운 구조
- 🌐 **확장성** - Blueprint로 모듈화 가능

이 AI Note System도 Flask로 만들어졌어요! Blueprint 패턴으로 깔끔하게 구성되어 있습니다."""

    elif any(word in message_lower for word in ['langchain', '랭체인']):
        response = """LangChain은 AI 애플리케이션 개발을 위한 강력한 프레임워크입니다!

**핵심 개념:**
- 🔗 **Chains** - AI 작업들을 연결
- 📚 **RAG** - 문서 검색 + 생성 결합
- 💾 **Memory** - 대화 맥락 유지
- 🎯 **Agents** - 도구를 활용하는 AI

이 프로젝트에서도 LangChain으로 노트 검색과 AI 채팅을 구현했어요!"""

    elif any(word in message_lower for word in ['도움', 'help', '기능']):
        response = """AI Note System 사용법을 알려드릴게요! 

**주요 기능:**
- 📝 **노트 작성** - 마크다운으로 멋진 노트 작성
- 🔍 **검색** - 제목, 내용, 태그로 노트 검색  
- 🏷️ **태그** - `#태그` 형태로 노트 분류
- 🤖 **AI 채팅** - 궁금한 것을 AI에게 질문

**API 엔드포인트:**
- `GET /api/notes` - 노트 목록
- `POST /api/notes` - 새 노트 생성
- `POST /api/chat` - AI와 대화

더 궁금한 게 있으면 언제든 물어보세요! 😊"""

    else:
        response = f""""{message}"에 대해 답변드리겠습니다.

현재는 Mock AI 모드로 동작하고 있습니다. 실제 Claude API를 사용하려면 .env 파일에 ANTHROPIC_API_KEY를 설정해주세요.

**이 시스템에서 가능한 질문들:**
- 마크다운 사용법
- Vue.js나 Python 관련 질문  
- 시스템 사용법
- 프로그래밍 관련 질문

더 구체적인 질문을 해주시면 더 도움이 될 수 있어요! 🤖"""
    
    return {
        "response": response,
        "model": "Mock AI (개발용)",
        "success": True
    }


@chat_bp.route('/', methods=['POST'])
def chat():
    """기본 AI 채팅"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        message = data['message'].strip()
        use_mock = data.get('use_mock', True)  # 기본값: Mock 사용
        
        # AI 응답 생성
        if use_mock or not Config.ANTHROPIC_API_KEY:
            result = get_mock_response(message)
        else:
            result = get_claude_response(message)
        
        return jsonify({
            "user_message": message,
            "ai_response": result["response"],
            "model": result["model"],
            "success": result["success"],
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"채팅 오류: {str(e)}"}), 500


@chat_bp.route('/test', methods=['GET'])
def test_claude():
    """Claude API 연결 테스트"""
    try:
        if not Config.ANTHROPIC_API_KEY:
            return jsonify({
                "status": "❌ API 키 없음",
                "message": "ANTHROPIC_API_KEY를 .env 파일에 설정해주세요",
                "mock_available": True
            }), 400
        
        # 간단한 테스트 메시지
        result = get_claude_response("안녕하세요! API 테스트입니다.")
        
        if result["success"]:
            return jsonify({
                "status": "✅ Claude API 연결 성공!",
                "response": result["response"][:100] + "...",
                "model": result["model"]
            })
        else:
            return jsonify({
                "status": "❌ Claude API 연결 실패",
                "error": result["response"],
                "mock_available": True
            }), 500
            
    except Exception as e:
        return jsonify({
            "status": "❌ 테스트 실패",
            "error": str(e),
            "mock_available": True
        }), 500


@chat_bp.route('/rag', methods=['POST'])
def chat_with_rag():
    """RAG 기반 채팅 (향후 구현)"""
    try:
        data = request.get_json()
        
        if not data or not data.get('message'):
            return jsonify({"error": "메시지를 입력해주세요"}), 400
        
        message = data['message'].strip()
        
        # 현재는 기본 채팅과 동일 (RAG 기능은 향후 구현)
        result = get_mock_response(f"[RAG 모드] {message}")
        
        return jsonify({
            "user_message": message,
            "ai_response": result["response"] + "\n\n*RAG 기능은 현재 개발 중입니다.",
            "model": "RAG + " + result["model"],
            "rag_enabled": False,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({"error": f"RAG 채팅 오류: {str(e)}"}), 500