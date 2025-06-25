# backend/app/services/chat_service.py
"""
ChatService - 채팅 관련 비즈니스 로직 (RAG 연결 완료)

RAG 시스템과 완전히 연결된 ChatController 호환 메서드들
"""

import logging
from datetime import datetime
from config.settings import Config
from models.note import ChatHistory, Note
from config.database import db
from chains.rag_chain import rag_chain

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
        RAG 기반 지능형 채팅 (실제 RAG 시스템 연결)
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
            
        Returns:
            dict: RAG 채팅 응답 데이터
        """
        if not message or not message.strip():
            raise ValueError("메시지가 비어있습니다")
        
        message = message.strip()
        
        # RAG 컨텍스트 검색
        context = ""
        relevant_notes = []
        rag_enabled = rag_chain.is_available()
        
        if rag_enabled:
            try:
                context = rag_chain.get_context_for_query(message, k=3)
                relevant_notes = rag_chain.search_similar_notes(message, k=3)
                
                # Claude에게 컨텍스트와 함께 질문
                rag_prompt = f"""다음은 사용자의 노트들에서 검색된 관련 정보입니다:

{context}

위 정보를 참고해서 다음 질문에 답변해주세요:
질문: {message}

답변 시 다음 사항을 지켜주세요:
1. 검색된 노트 내용을 활용해 구체적으로 답변
2. 노트에 없는 내용은 일반적인 지식으로 보완
3. 한국어로 친근하게 답변
4. 관련 노트가 없다면 일반적인 답변 제공

답변:"""
                
                logger.info(f"RAG 검색 완료: {len(relevant_notes)}개 관련 노트 발견")
                
            except Exception as rag_error:
                logger.error(f"RAG 검색 오류: {rag_error}")
                rag_prompt = f"[RAG 검색 실패] {message}"
                context = "RAG 검색 중 오류가 발생했습니다."
                
        else:
            rag_prompt = f"[RAG 시스템 사용 불가] {message}"
            context = "RAG 시스템이 현재 사용할 수 없습니다."
        
        # AI 응답 생성
        if not self.api_key:
            ai_result = self._get_mock_rag_response(message, relevant_notes)
        else:
            try:
                ai_result = self._get_claude_response(rag_prompt)
            except Exception as claude_error:
                logger.warning(f"Claude API 실패, Mock으로 폴백: {claude_error}")
                ai_result = self._get_mock_rag_response(message, relevant_notes)
        
        # 결과 구성
        result = {
            "user_message": message,
            "ai_response": ai_result["response"],
            "model": "RAG + " + ai_result["model"],
            "success": ai_result["success"],
            "rag_enabled": rag_enabled,
            "relevant_notes": [
                {
                    "note_id": note["note_id"],
                    "title": note["title"],
                    "content_preview": note["content_preview"],
                    "similarity_score": round(note["similarity_score"], 3)
                } for note in relevant_notes
            ],
            "context_length": len(context),
            "search_query": message,
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
        """RAG 시스템 상태 확인 (실제 상태 반환)"""
        try:
            rag_stats = rag_chain.get_stats()
            
            return {
                "rag_status": {
                    "available": rag_stats["available"],
                    "reason": "정상 동작" if rag_stats["available"] else "패키지 미설치 또는 초기화 실패"
                },
                "vector_store": {
                    "indexed_notes": rag_stats["indexed_notes"],
                    "vector_count": rag_stats["vector_count"],
                    "last_updated": datetime.now().isoformat() if rag_stats["indexed_notes"] > 0 else None
                },
                "embeddings_model": rag_stats["model_name"],
                "model_dimension": rag_stats["dimension"],
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG 상태 확인 오류: {e}")
            return {
                "rag_status": {
                    "available": False,
                    "reason": f"상태 확인 실패: {str(e)}"
                },
                "vector_store": {
                    "indexed_notes": 0,
                    "last_updated": None
                },
                "embeddings_model": None,
                "timestamp": datetime.now().isoformat()
            }
    
    def rebuild_rag_index(self) -> dict:
        """RAG 인덱스 재구축 (실제 구현)"""
        try:
            if not rag_chain.is_available():
                return {
                    "status": "error",
                    "message": "RAG 시스템이 사용 불가능합니다",
                    "progress": 0,
                    "timestamp": datetime.now().isoformat()
                }
            
            # 모든 노트 조회
            notes = Note.query.all()
            note_data = [
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content
                }
                for note in notes
            ]
            
            logger.info(f"RAG 인덱스 재구축 시작: {len(note_data)}개 노트")
            
            # 인덱스 재구축
            success = rag_chain.rebuild_index(note_data)
            
            if success:
                return {
                    "status": "success",
                    "message": f"RAG 인덱스 재구축 완료: {len(note_data)}개 노트 처리",
                    "progress": 100,
                    "indexed_notes": len(note_data),
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "status": "error",
                    "message": "RAG 인덱스 재구축 실패",
                    "progress": 0,
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            logger.error(f"RAG 인덱스 재구축 오류: {e}")
            return {
                "status": "error",
                "message": f"인덱스 재구축 중 오류: {str(e)}",
                "progress": 0,
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
- `POST /api/chat` - AI와 대화

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
    
    def _get_mock_rag_response(self, message: str, relevant_notes: list) -> dict:
        """RAG용 Mock 응답 생성"""
        if relevant_notes:
            notes_summary = ", ".join([note["title"] for note in relevant_notes[:3]])
            response = f"""[RAG 모드 - Mock] "{message}"에 대해 검색된 관련 노트들을 참고해서 답변드립니다.

🔍 **검색된 관련 노트:** {notes_summary}

검색된 노트들의 내용을 종합하면, 당신의 질문과 관련된 유용한 정보들이 있습니다. 실제 Claude API가 연결되면 이 노트들의 내용을 바탕으로 더 정확하고 구체적인 답변을 제공할 수 있습니다.

💡 **RAG 시스템 동작 확인:**
- 벡터 검색: ✅ 완료 ({len(relevant_notes)}개 노트 발견)
- 컨텍스트 생성: ✅ 완료
- AI 응답 생성: 🔄 Mock 모드

Claude API 키를 설정하시면 실제 AI 기반 응답을 받으실 수 있습니다! 🤖"""
        else:
            response = f"""[RAG 모드 - Mock] "{message}"에 대해 검색했지만 관련된 노트를 찾을 수 없습니다.

🔍 **검색 결과:** 관련 노트 없음

새로운 노트를 작성하신 후 다시 질문해보시거나, 다른 키워드로 질문해보세요.

💡 **RAG 시스템 동작 확인:**
- 벡터 검색: ✅ 완료 (관련 노트 없음)
- 일반 AI 응답: 🔄 Mock 모드

노트를 더 많이 작성하시면 더 정확한 RAG 검색이 가능합니다! 📝"""
        
        return {
            "response": response,
            "model": "Mock RAG AI (개발용)",
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