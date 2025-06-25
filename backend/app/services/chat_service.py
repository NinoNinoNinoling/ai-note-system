# backend/app/services/chat_service.py
"""
완전히 수정된 ChatService - 모든 메서드 구현 완료

✅ 수정사항:
1. search_chat_history 메서드 추가
2. get_chat_summary 메서드 추가  
3. export_chat_history 메서드 추가
4. 빈 메시지 처리 개선 (400 오류)
5. 모든 누락된 메서드 구현
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from config.settings import Config
from models.note import ChatHistory, Note
from config.database import db
from chains.rag_chain import rag_chain

logger = logging.getLogger(__name__)


class ChatService:
    """완성된 채팅 서비스 클래스"""
    
    def __init__(self):
        self.api_key = Config.ANTHROPIC_API_KEY
    
    # =========================
    # 기본 채팅 기능
    # =========================
    
    def basic_chat(self, message: str, save_history: bool = True) -> dict:
        """
        기본 AI 채팅 - 빈 메시지 처리 개선
        
        Args:
            message: 사용자 메시지
            save_history: 히스토리 저장 여부
            
        Returns:
            dict: 채팅 응답 데이터
        """
        # ✅ 빈 메시지 처리 개선 - 400 오류로 처리
        if not message:
            raise ValueError("메시지가 필요합니다")
        
        message = message.strip()
        if not message:
            raise ValueError("빈 메시지나 공백만 있는 메시지는 처리할 수 없습니다")
        
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
            "timestamp": self._get_timestamp()
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
        if not message:
            raise ValueError("메시지가 필요합니다")
        
        message = message.strip()
        if not message:
            raise ValueError("빈 메시지나 공백만 있는 메시지는 처리할 수 없습니다")
        
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
4. 관련된 노트가 있다면 참고했다고 언급"""
                
                if self.api_key:
                    try:
                        ai_result = self._get_claude_response(rag_prompt)
                    except Exception:
                        ai_result = self._get_mock_response(rag_prompt)
                else:
                    ai_result = self._get_mock_response(rag_prompt)
                    
            except Exception as rag_error:
                logger.warning(f"RAG 검색 실패, 기본 채팅으로 폴백: {rag_error}")
                return self.basic_chat(message, save_history)
        else:
            # RAG 사용 불가시 기본 채팅
            return self.basic_chat(message, save_history)
        
        # 결과 구성
        result = {
            "user_message": message,
            "ai_response": ai_result["response"],
            "model": ai_result["model"],
            "success": ai_result["success"],
            "rag_enabled": True,
            "context_used": len(context) > 0,
            "relevant_notes_count": len(relevant_notes),
            "relevant_notes": [note.get('title', 'Untitled') for note in relevant_notes[:3]],
            "timestamp": self._get_timestamp()
        }
        
        # 히스토리 저장
        if save_history:
            self._save_chat_history(
                user_message=message,
                ai_response=ai_result["response"],
                model=f"{ai_result['model']} (RAG)"
            )
        
        return result
    
    def test_claude_connection(self) -> dict:
        """Claude API 연결 테스트"""
        try:
            test_result = self.basic_chat("Claude API 연결 테스트입니다.", save_history=False)
            
            if test_result["success"]:
                return {
                    "status": "success",
                    "message": "Claude API 연결 성공",
                    "response": test_result["ai_response"][:100] + "...",
                    "model": test_result["model"]
                }
            else:
                return {
                    "status": "error",
                    "message": "Claude API 연결 실패",
                    "response": test_result["ai_response"],
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
    
    # =========================
    # ✅ 채팅 히스토리 기능 (완전 구현)
    # =========================
    
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
    
    def clear_chat_history(self) -> int:
        """채팅 히스토리 삭제"""
        try:
            # 모든 채팅 기록 개수 조회
            total_count = ChatHistory.query.count()
            
            # 모든 채팅 기록 삭제
            ChatHistory.query.delete()
            db.session.commit()
            
            logger.info(f"채팅 히스토리 {total_count}개 삭제 완료")
            return total_count
            
        except Exception as e:
            logger.error(f"채팅 히스토리 삭제 실패: {e}")
            db.session.rollback()
            return 0
    
    def search_chat_history(self, query: str, limit: int = 10) -> list:
        """✅ 채팅 히스토리 검색 (새로 추가된 메서드)"""
        try:
            if not query or not query.strip():
                return []
            
            query_pattern = f"%{query.strip()}%"
            
            # 사용자 메시지나 AI 응답에서 검색
            results = ChatHistory.query.filter(
                db.or_(
                    ChatHistory.user_message.ilike(query_pattern),
                    ChatHistory.ai_response.ilike(query_pattern)
                )
            ).order_by(
                ChatHistory.created_at.desc()
            ).limit(limit).all()
            
            return [chat.to_dict() for chat in results]
            
        except Exception as e:
            logger.error(f"채팅 히스토리 검색 실패: {e}")
            return []
    
    def get_chat_summary(self, days: int = 7) -> dict:
        """✅ 채팅 요약 통계 (새로 추가된 메서드)"""
        try:
            # 지정된 일수 이전 날짜 계산
            start_date = datetime.now() - timedelta(days=days)
            
            # 기간 내 채팅 수
            period_chats = ChatHistory.query.filter(
                ChatHistory.created_at >= start_date
            ).count()
            
            # 일별 채팅 수
            daily_stats = {}
            for i in range(days):
                day = datetime.now() - timedelta(days=i)
                day_str = day.strftime('%Y-%m-%d')
                
                day_count = ChatHistory.query.filter(
                    db.func.date(ChatHistory.created_at) == day.date()
                ).count()
                
                daily_stats[day_str] = day_count
            
            # 가장 활발한 시간대 (시간별 통계)
            hour_stats = {}
            hour_results = db.session.query(
                db.func.extract('hour', ChatHistory.created_at).label('hour'),
                db.func.count(ChatHistory.id).label('count')
            ).filter(
                ChatHistory.created_at >= start_date
            ).group_by('hour').all()
            
            for hour, count in hour_results:
                hour_stats[f"{int(hour):02d}:00"] = count
            
            # 평균 메시지 길이
            recent_chats = ChatHistory.query.filter(
                ChatHistory.created_at >= start_date
            ).all()
            
            avg_user_length = 0
            avg_ai_length = 0
            
            if recent_chats:
                user_lengths = [len(chat.user_message or '') for chat in recent_chats]
                ai_lengths = [len(chat.ai_response or '') for chat in recent_chats]
                
                avg_user_length = round(sum(user_lengths) / len(user_lengths))
                avg_ai_length = round(sum(ai_lengths) / len(ai_lengths))
            
            return {
                "period_days": days,
                "total_chats": period_chats,
                "daily_stats": daily_stats,
                "hourly_stats": hour_stats,
                "average_message_length": {
                    "user": avg_user_length,
                    "ai": avg_ai_length
                },
                "most_active_day": max(daily_stats.items(), key=lambda x: x[1])[0] if daily_stats else None,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"채팅 요약 통계 실패: {e}")
            return {
                "period_days": days,
                "total_chats": 0,
                "error": str(e),
                "timestamp": self._get_timestamp()
            }
    
    def export_chat_history(self, start_date: Optional[str] = None, end_date: Optional[str] = None) -> dict:
        """✅ 채팅 히스토리 내보내기 (새로 추가된 메서드)"""
        try:
            query = ChatHistory.query
            
            # 날짜 필터링
            if start_date:
                try:
                    start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
                    query = query.filter(ChatHistory.created_at >= start_dt)
                except:
                    start_dt = datetime.fromisoformat(start_date)
                    query = query.filter(ChatHistory.created_at >= start_dt)
            
            if end_date:
                try:
                    end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
                    query = query.filter(ChatHistory.created_at <= end_dt)
                except:
                    end_dt = datetime.fromisoformat(end_date)
                    query = query.filter(ChatHistory.created_at <= end_dt)
            
            # 모든 채팅 기록 조회
            chat_records = query.order_by(ChatHistory.created_at.asc()).all()
            
            # 내보내기 데이터 구성
            export_data = {
                "export_info": {
                    "generated_at": self._get_timestamp(),
                    "total_records": len(chat_records),
                    "date_range": {
                        "start": start_date,
                        "end": end_date
                    }
                },
                "chat_history": [
                    {
                        "id": chat.id,
                        "user_message": chat.user_message,
                        "ai_response": chat.ai_response,
                        "model_used": chat.model_used,
                        "created_at": chat.created_at.isoformat()
                    }
                    for chat in chat_records
                ]
            }
            
            return {
                "success": True,
                "data": export_data,
                "message": f"{len(chat_records)}개의 채팅 기록을 내보냈습니다"
            }
            
        except Exception as e:
            logger.error(f"채팅 히스토리 내보내기 실패: {e}")
            return {
                "success": False,
                "error": str(e),
                "data": None,
                "message": "내보내기 실패"
            }
    
    # =========================
    # ✅ 통계 기능 (완전 구현)
    # =========================
    
    def get_chat_stats(self) -> dict:
        """채팅 통계 정보"""
        try:
            # 기본 통계
            total_chats = ChatHistory.query.count()
            
            # 최근 7일 채팅 수
            week_ago = datetime.now() - timedelta(days=7)
            recent_chats = ChatHistory.query.filter(
                ChatHistory.created_at >= week_ago
            ).count()
            
            # 오늘 채팅 수
            today = datetime.now().date()
            today_chats = ChatHistory.query.filter(
                db.func.date(ChatHistory.created_at) == today
            ).count()
            
            # 모델별 사용 통계
            model_stats = {}
            model_results = db.session.query(
                ChatHistory.model_used,
                db.func.count(ChatHistory.id).label('count')
            ).group_by(ChatHistory.model_used).all()
            
            for model, count in model_results:
                model_stats[model or 'Unknown'] = count
            
            # 평균 응답 길이 (최근 100개)
            recent_responses = ChatHistory.query.order_by(
                ChatHistory.created_at.desc()
            ).limit(100).all()
            
            avg_response_length = 0
            if recent_responses:
                total_length = sum(len(chat.ai_response or '') for chat in recent_responses)
                avg_response_length = round(total_length / len(recent_responses))
            
            return {
                "total_chats": total_chats,
                "recent_chats_7d": recent_chats,
                "today_chats": today_chats,
                "model_usage": model_stats,
                "average_response_length": avg_response_length,
                "rag_enabled": rag_chain.is_available(),
                "claude_connected": bool(self.api_key),
                "last_chat": recent_responses[0].created_at.isoformat() if recent_responses else None,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"채팅 통계 조회 실패: {e}")
            return {
                "total_chats": 0,
                "error": f"통계 조회 실패: {str(e)}",
                "timestamp": self._get_timestamp()
            }
    
    # =========================
    # RAG 관련 기능
    # =========================
    
    def get_rag_status(self) -> dict:
        """RAG 시스템 상태 확인"""
        try:
            rag_available = rag_chain.is_available()
            
            status = {
                "rag_status": {
                    "available": rag_available,
                    "index_path": rag_chain.index_path if rag_available else None,
                    "metadata_path": rag_chain.metadata_path if rag_available else None
                },
                "note_count": 0,
                "indexed_notes": 0,
                "last_updated": None
            }
            
            if rag_available:
                try:
                    # 노트 개수 확인
                    total_notes = Note.query.count()
                    status["note_count"] = total_notes
                    
                    # 인덱싱된 노트 수 (실제 인덱스에서)
                    indexed_count = rag_chain.get_indexed_count()
                    status["indexed_notes"] = indexed_count
                    
                    # 마지막 업데이트 시간
                    last_update = rag_chain.get_last_update_time()
                    status["last_updated"] = last_update
                    
                except Exception as detail_error:
                    logger.warning(f"RAG 세부 정보 조회 실패: {detail_error}")
            
            return status
            
        except Exception as e:
            logger.error(f"RAG 상태 확인 실패: {e}")
            return {
                "rag_status": {"available": False, "error": str(e)},
                "note_count": 0,
                "indexed_notes": 0,
                "last_updated": None
            }
    
    def rebuild_rag_index(self) -> dict:
        """RAG 인덱스 재구축"""
        try:
            if not rag_chain.is_available():
                return {
                    "success": False,
                    "message": "RAG 시스템을 사용할 수 없습니다"
                }
            
            # 모든 노트 조회
            notes = Note.query.all()
            
            # 인덱스 재구축
            rebuilt_count = rag_chain.rebuild_index([note.to_dict() for note in notes])
            
            return {
                "success": True,
                "message": f"RAG 인덱스 재구축 완료",
                "notes_processed": len(notes),
                "notes_indexed": rebuilt_count,
                "timestamp": self._get_timestamp()
            }
            
        except Exception as e:
            logger.error(f"RAG 인덱스 재구축 실패: {e}")
            return {
                "success": False,
                "message": f"인덱스 재구축 실패: {str(e)}",
                "notes_processed": 0,
                "notes_indexed": 0
            }
    
    # =========================
    # 내부 헬퍼 메서드들
    # =========================
    
    def _get_claude_response(self, message: str) -> dict:
        """Claude API 호출"""
        try:
            from anthropic import Anthropic
            
            client = Anthropic(api_key=self.api_key)
            
            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                messages=[{
                    "role": "user",
                    "content": message
                }]
            )
            
            return {
                "success": True,
                "response": response.content[0].text,
                "model": "claude-3-sonnet"
            }
            
        except Exception as e:
            logger.error(f"Claude API 오류: {e}")
            return {
                "success": False,
                "response": f"Claude API 오류: {str(e)}",
                "model": "claude-3-sonnet (error)"
            }
    
    def _get_mock_response(self, message: str) -> dict:
        """Mock 응답 생성 (Claude API 없을 때)"""
        mock_responses = [
            f"안녕하세요! '{message}'에 대한 질문을 받았습니다. 이것은 Mock 응답입니다.",
            f"'{message}'에 대해 도움을 드리고 싶지만, 현재 Claude API가 연결되지 않아 Mock 응답을 제공합니다.",
            f"질문 '{message}'에 대한 Mock 답변입니다. 실제 Claude API 키를 설정하면 더 나은 응답을 받을 수 있습니다."
        ]
        
        import random
        selected_response = random.choice(mock_responses)
        
        return {
            "success": True,
            "response": selected_response,
            "model": "mock-assistant"
        }
    
    def _save_chat_history(self, user_message: str, ai_response: str, model: str):
        """채팅 기록 저장"""
        try:
            chat_record = ChatHistory(
                user_message=user_message,
                ai_response=ai_response,
                model_used=model
            )
            
            db.session.add(chat_record)
            db.session.commit()
            
            logger.debug(f"Chat history saved: {chat_record.id}")
            
        except Exception as e:
            logger.error(f"채팅 기록 저장 실패: {e}")
            db.session.rollback()
    
    def _get_timestamp(self) -> str:
        """현재 타임스탬프 반환"""
        return datetime.now().isoformat()
    
    def _get_db_connection(self):
        """데이터베이스 연결 반환 (호환성)"""
        return db.session