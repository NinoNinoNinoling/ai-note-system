# backend/app/services/chat_service.py
"""
ChatService - 채팅 관련 비즈니스 로직

기본 AI 채팅, RAG 기반 채팅, 채팅 히스토리 관리
"""

from config.settings import Config
from models.note import ChatHistory, Note
from config.database import db
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ChatService:
    """채팅 비즈니스 로직 서비스"""
    
    def __init__(self):
        self.rag_available = False
        self.rag_chain = None
        
        # RAG 시스템 초기화
        self._initialize_rag()
    
    def _initialize_rag(self):
        """RAG 시스템 초기화"""
        try:
            from chains.rag_chain import rag_chain, RAG_AVAILABLE
            
            if RAG_AVAILABLE and rag_chain and rag_chain.is_available():
                self.rag_chain = rag_chain
                self.rag_available = True
                logger.info("✅ RAG 시스템 연결 성공")
            else:
                logger.warning("⚠️ RAG 시스템 사용 불가 - 패키지 설치 필요")
                
        except ImportError as e:
            logger.warning(f"⚠️ RAG 시스템 임포트 실패: {e}")
    
    def basic_chat(self, message: str, save_history=True) -> dict:
        """
        기본 AI 채팅
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
        """
        try:
            if not message or not message.strip():
                raise ValueError("메시지를 입력해주세요")
            
            message = message.strip()
            
            # Claude API 또는 Mock 응답
            result = self._get_ai_response(message)
            
            # 채팅 히스토리 저장
            if save_history:
                self._save_chat_history(
                    user_message=message,
                    ai_response=result["response"],
                    model_used=result["model"]
                )
            
            return {
                "user_message": message,
                "ai_response": result["response"],
                "model": result["model"],
                "rag_enabled": False,
                "timestamp": datetime.now().isoformat()
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Basic chat error: {e}")
            raise Exception(f"채팅 처리 중 오류가 발생했습니다: {str(e)}")
    
    def rag_chat(self, message: str, save_history=True) -> dict:
        """
        RAG 기반 지능형 채팅
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
        """
        try:
            if not message or not message.strip():
                raise ValueError("메시지를 입력해주세요")
            
            message = message.strip()
            
            if not self.rag_available:
                # RAG가 없으면 기본 채팅으로 대체
                result = self.basic_chat(message, save_history=False)
                result["ai_response"] += "\n\n⚠️ RAG 시스템이 비활성화되어 있어 기본 응답을 제공했습니다."
                result["rag_enabled"] = False
                
                if save_history:
                    self._save_chat_history(
                        user_message=message,
                        ai_response=result["ai_response"],
                        model_used="Basic + RAG Disabled"
                    )
                
                return result
            
            # RAG 검색 수행
            search_results = self.rag_chain.search_similar(message, top_k=3)
            
            if not search_results:
                # 관련 노트가 없으면 기본 응답
                result = self.basic_chat(message, save_history=False)
                result["ai_response"] += "\n\n💡 관련된 노트를 찾지 못했습니다. 더 많은 노트를 작성하시면 더 정확한 답변을 드릴 수 있어요!"
                result["rag_enabled"] = True
                result["context_notes"] = []
            else:
                # 컨텍스트 구성
                context = self._build_context(search_results)
                
                # RAG 기반 응답 생성
                rag_prompt = self._build_rag_prompt(message, context)
                result = self._get_ai_response(rag_prompt)
                
                result = {
                    "user_message": message,
                    "ai_response": result["response"],
                    "model": f"RAG + {result['model']}",
                    "rag_enabled": True,
                    "context_notes": [
                        {
                            "note_id": note["note_id"],
                            "title": note["title"],
                            "similarity": note["similarity"],
                            "preview": note["content_preview"]
                        }
                        for note in search_results
                    ],
                    "timestamp": datetime.now().isoformat()
                }
            
            # 채팅 히스토리 저장
            if save_history:
                self._save_chat_history(
                    user_message=message,
                    ai_response=result["ai_response"],
                    model_used=result["model"]
                )
            
            return result
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"RAG chat error: {e}")
            raise Exception(f"RAG 채팅 처리 중 오류가 발생했습니다: {str(e)}")
    
    def get_rag_status(self) -> dict:
        """RAG 시스템 상태 조회"""
        try:
            if not self.rag_available:
                return {
                    "rag_status": {
                        "available": False,
                        "reason": "RAG 패키지가 설치되지 않았습니다",
                        "required_packages": ["faiss-cpu", "sentence-transformers", "numpy"]
                    },
                    "stats": None
                }
            
            # RAG 통계 정보
            stats = self.rag_chain.get_stats()
            
            return {
                "rag_status": {
                    "available": True,
                    "model_name": "paraphrase-multilingual-MiniLM-L12-v2",
                    "last_updated": datetime.now().isoformat()
                },
                "stats": stats
            }
            
        except Exception as e:
            logger.error(f"RAG status error: {e}")
            return {
                "rag_status": {
                    "available": False,
                    "reason": f"RAG 상태 확인 오류: {str(e)}"
                },
                "stats": None
            }
    
    def rebuild_rag_index(self) -> dict:
        """RAG 인덱스 재구축"""
        try:
            if not self.rag_available:
                raise Exception("RAG 시스템이 사용 불가능합니다")
            
            # 모든 노트 가져오기
            notes = Note.query.all()
            
            if not notes:
                return {
                    "message": "인덱싱할 노트가 없습니다",
                    "indexed_count": 0
                }
            
            # 인덱스 재구축
            success_count = 0
            for note in notes:
                if self.rag_chain.add_note(note.id, note.title, note.content):
                    success_count += 1
            
            return {
                "message": f"RAG 인덱스 재구축 완료",
                "indexed_count": success_count,
                "total_notes": len(notes),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"RAG index rebuild error: {e}")
            raise Exception(f"RAG 인덱스 재구축 실패: {str(e)}")
    
    def test_claude_connection(self) -> dict:
        """Claude API 연결 테스트"""
        try:
            test_message = "안녕하세요! 연결 테스트입니다."
            result = self._get_ai_response(test_message)
            
            return {
                "status": "success" if result["success"] else "failed",
                "response": result["response"][:200] + "..." if len(result["response"]) > 200 else result["response"],
                "model": result["model"],
                "api_available": result["success"]
            }
            
        except Exception as e:
            logger.error(f"Claude test error: {e}")
            return {
                "status": "failed",
                "response": f"테스트 실패: {str(e)}",
                "model": "Error",
                "api_available": False
            }
    
    def get_chat_history(self, limit=20) -> list:
        """채팅 히스토리 조회"""
        try:
            history = ChatHistory.get_recent_chats(limit=limit)
            return [chat.to_dict() for chat in history]
        except Exception as e:
            logger.error(f"Chat history error: {e}")
            raise Exception(f"채팅 히스토리 조회 실패: {str(e)}")
    
    def _get_ai_response(self, message: str) -> dict:
        """Claude API 또는 Mock 응답"""
        try:
            if not Config.ANTHROPIC_API_KEY:
                return self._get_mock_response(message)
            
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
            logger.warning(f"Claude API error: {e}")
            return self._get_mock_response(message)
    
    def _get_mock_response(self, message: str) -> dict:
        """Mock AI 응답"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ['안녕', 'hello', '헬로']):
            response = "안녕하세요! AI Note System의 AI 어시스턴트입니다. 무엇을 도와드릴까요?"
        elif any(word in message_lower for word in ['노트', 'note']):
            response = "노트 시스템에 대해 궁금한 것이 있으시군요! 마크다운으로 노트를 작성하고, 태그로 분류하며, AI와 대화할 수 있는 시스템입니다."
        elif any(word in message_lower for word in ['rag', '검색']):
            response = "RAG(Retrieval-Augmented Generation)는 검색과 생성을 결합한 AI 기술입니다. 여러분의 노트를 검색해서 더 정확한 답변을 제공합니다!"
        elif any(word in message_lower for word in ['도움', 'help']):
            response = """AI Note System 사용법:
1. 📝 노트 작성: 마크다운으로 노트 작성
2. 🏷️ 태그 사용: #태그로 분류
3. 🔍 검색: 제목, 내용, 태그로 검색
4. 💬 AI 채팅: 노트 기반 지능형 대화"""
        else:
            response = f"'{message}'에 대해 말씀해주셨네요. 더 구체적인 질문을 해주시면 더 도움이 될 것 같아요!"
        
        return {
            "response": response,
            "model": "Mock AI",
            "success": False
        }
    
    def _build_context(self, search_results: list) -> str:
        """검색 결과로 컨텍스트 구성"""
        if not search_results:
            return ""
        
        context_parts = []
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"""노트 {i}: {result['title']}
{result['full_content'][:500]}{'...' if len(result['full_content']) > 500 else ''}
""")
        
        return "\n---\n".join(context_parts)
    
    def _build_rag_prompt(self, user_question: str, context: str) -> str:
        """RAG 프롬프트 구성"""
        return f"""다음은 사용자의 개인 노트들입니다:

{context}

---

위의 노트 내용을 참고해서 다음 질문에 답해주세요:
질문: {user_question}

답변 시 주의사항:
1. 노트 내용을 바탕으로 정확하게 답변해주세요
2. 노트에 없는 내용은 일반적인 지식으로 보완해주세요
3. 어떤 노트를 참고했는지 언급해주세요
4. 친근하고 도움이 되는 톤으로 답변해주세요"""
    
    def _save_chat_history(self, user_message: str, ai_response: str, model_used: str, note_id: int = None):
        """채팅 히스토리 저장"""
        try:
            history = ChatHistory(
                note_id=note_id,
                user_message=user_message,
                ai_response=ai_response,
                model_used=model_used
            )
            
            db.session.add(history)
            db.session.commit()
            
            logger.info(f"Chat history saved: {history.id}")
            
        except Exception as e:
            logger.error(f"Failed to save chat history: {e}")
            db.session.rollback()