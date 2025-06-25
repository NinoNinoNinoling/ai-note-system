# backend/app/services/chat_service.py
"""
ChatService - 채팅 관련 비즈니스 로직 (프로덕션 버전)

깔끔하게 정리된 ChatController 호환 메서드들
"""

import logging
from datetime import datetime
from config.settings import Config
from models.note import ChatHistory
from config.database import db

logger = logging.getLogger(__name__)


class ChatService:
    """채팅 서비스 클래스"""
    
    def __init__(self):
        self.api_key = Config.ANTHROPIC_API_KEY
    
    def basic_chat(self, message: str, save_history: bool = True) -> dict:
        """
        기본 AI 채팅
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
            
        Returns:
            dict: 채팅 응답 데이터
        """
        if not message or not message.strip():
            raise ValueError("메시지가 비어있습니다")
        
        message = message.strip()
        
        # AI 응답 생성
        if not self.api_key:
            ai_result = self._get_mock_response(message)
        else:
            try:
                ai_result = self._get_claude_response(message)
            except Exception as claude_error:
                logger.warning(f"Claude API 실패, Mock으로 폴백: {claude_error}")
                ai_result = self._get_mock_response(message)
        
        # 응답 데이터 구성
        result = {
            "user_message": message,
            "ai_response": ai_result["response"],
            "model": ai_result["model"],
            "success": ai_result["success"],
            "timestamp": datetime.now().isoformat()
        }
        
        # 히스토리 저장
        if save_history:
            self._save_chat_history(
                user_message=message,
                ai_response=ai_result["response"],
                model=ai_result["model"]
            )
        
        return result
    
    def rag_chat(self, message: str, save_history: bool = True) -> dict:
        """
        RAG 기반 지능형 채팅
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
            
        Returns:
            dict: RAG 채팅 응답 데이터
        """
        if not message or not message.strip():
            raise ValueError("메시지가 비어있습니다")
        
        message = message.strip()
        
        # 현재는 기본 채팅과 동일 (향후 실제 RAG 구현 예정)
        rag_message = f"[RAG 모드] {message}"
        
        if not self.api_key:
            ai_result = self._get_mock_response(rag_message)
        else:
            try:
                ai_result = self._get_claude_response(rag_message)
            except Exception as claude_error:
                logger.warning(f"Claude API 실패, Mock으로 폴백: {claude_error}")
                ai_result = self._get_mock_response(rag_message)
        
        # RAG 메타데이터 추가
        result = {
            "user_message": message,
            "ai_response": ai_result["response"] + "\n\n*RAG 기능은 현재 개발 중입니다.",
            "model": "RAG + " + ai_result["model"],
            "success": ai_result["success"],
            "rag_enabled": False,  # 현재는 비활성화
            "relevant_notes": [],  # 향후 구현
            "timestamp": datetime.now().isoformat()
        }
        
        # 히스토리 저장
        if save_history:
            self._save_chat_history(
                user_message=message,
                ai_response=result["ai_response"],
                model=result["model"]
            )
        
        return result
    
    def get_rag_status(self) -> dict:
        """RAG 시스템 상태 확인"""
        return {
            "rag_status": {
                "available": False,
                "reason": "RAG 시스템 구현 예정"
            },
            "vector_store": {
                "indexed_notes": 0,
                "last_updated": None
            },
            "embeddings_model": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def rebuild_rag_index(self) -> dict:
        """RAG 인덱스 재구축"""
        return {
            "status": "pending",
            "message": "RAG 인덱스 재구축 기능은 구현 예정입니다",
            "progress": 0,
            "estimated_time": None,
            "timestamp": datetime.now().isoformat()
        }
    
    def test_claude_connection(self) -> dict:
        """Claude API 연결 테스트"""
        if not self.api_key:
            return {
                "status": "error",
                "message": "ANTHROPIC_API_KEY가 설정되지 않았습니다",
                "response": "API 키를 .env 파일에 설정해주세요",
                "mock_available": True
            }
        
        try:
            # 간단한 테스트 메시지
            test_result = self._get_claude_response("안녕하세요! API 테스트입니다.")
            
            if test_result["success"]:
                return {
                    "status": "success",
                    "message": "Claude API 연결 성공",
                    "response": test_result["response"][:100] + "...",
                    "model": test_result["model"]
                }
            else:
                return {
                    "status": "error",
                    "message": "Claude API 연결 실패",
                    "response": test_result["response"],
                    "mock_available": True
                }
                
        except Exception as e:
            logger.error(f"Claude test error: {str(e)}")
            return {
                "status": "error",
                "message": "Claude API 테스트 중 오류 발생",
                "response": str(e),
                "mock_available": True
            }
    
    def get_chat_history(self, limit: int = 20) -> list:
        """채팅 히스토리 조회"""
        try:
            chat_records = ChatHistory.query.order_by(
                ChatHistory.created_at.desc()
            ).limit(limit).all()
            
            return [chat.to_dict() for chat in chat_records]
            
        except Exception as e:
            logger.error(f"Chat history error: {str(e)}")
            return []
    
    def _get_claude_response(self, message: str) -> dict:
        """Claude API 호출"""
        from anthropic import Anthropic
        
        client = Anthropic(api_key=self.api_key)
        
        response = client.messages.create(
            model="claude-3-5-sonnet-20240620",
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
    
    def _get_mock_response(self, message: str) -> dict:
        """Mock AI 응답 생성"""
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
- `POST /api/` - AI와 대화

더 궁금한 게 있으면 언제든 물어보세요! 😊"""

        else:
            response = f""""{message}"에 대해 답변드리겠습니다.

AI Note System에서는 다양한 질문에 답변해드릴 수 있습니다:
- 📝 마크다운 사용법
- 💻 프로그래밍 관련 질문  
- 🤖 시스템 사용법
- 📚 일반적인 학습 내용

더 구체적인 질문을 해주시면 더 도움이 될 수 있어요! 🤖"""
        
        return {
            "response": response,
            "model": "Mock AI (개발용)",
            "success": True
        }
    
    def _save_chat_history(self, user_message: str, ai_response: str, model: str):
        """채팅 히스토리 저장"""
        try:
            chat_record = ChatHistory(
                user_message=user_message,
                ai_response=ai_response,
                model_used=model
            )
            
            db.session.add(chat_record)
            db.session.commit()
            
        except Exception as e:
            logger.error(f"Failed to save chat history: {str(e)}")
            db.session.rollback()