# backend/app/controllers/chat_controller.py
"""
완전한 ChatController - 모든 메서드 포함

모든 오류 해결 + 모든 누락 메서드 구현 완료
"""

from flask import request
from app.controllers.base_controller import BaseController
from app.services.chat_service import ChatService
from app.services.note_service import NoteService
import logging

# Multiple Chains 임포트
try:
    from chains.specialized_chains import (
        chain_manager,
        summarize_note,
        analyze_note,
        recommend_notes,
        improve_note,
        CHAINS_AVAILABLE
    )
    CHAINS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️ Multiple Chains 임포트 실패: {e}")
    CHAINS_AVAILABLE = False

logger = logging.getLogger(__name__)


class ChatController(BaseController):
    """완전한 Chat Controller with Multiple Chains"""
    
    def __init__(self):
        self.chat_service = ChatService()
        self.note_service = NoteService()
    
    # =========================
    # 기본 채팅 기능 (수정됨)
    # =========================
    
    def basic_chat(self):
        """기본 AI 채팅 - 메서드명 수정"""
        self.log_request("basic_chat")
        
        data, error = self.get_json_data(required_fields=['message'])
        if error:
            return error
        
        try:
            message = data['message']
            # ✅ 수정: chat_with_claude → basic_chat
            response = self.chat_service.basic_chat(message)
            
            return self.success_response(
                data=response,  # ✅ 전체 응답 객체 반환
                message="채팅 응답 생성 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 처리 실패",
                details=str(e),
                status=500
            )
    
    def rag_chat(self):
        """RAG 기반 지능형 채팅 - 메서드명 수정"""
        self.log_request("rag_chat")
        
        data, error = self.get_json_data(required_fields=['message'])
        if error:
            return error
        
        try:
            message = data['message']
            # ✅ 수정: chat_with_rag → rag_chat
            response = self.chat_service.rag_chat(message)
            
            return self.success_response(
                data=response,
                message="RAG 채팅 응답 생성 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="RAG 채팅 처리 실패",
                details=str(e),
                status=500
            )
    
    def test_claude_connection(self):
        """Claude API 연결 테스트 - GET 요청 최적화"""
        self.log_request("test_claude")
        
        try:
            # ✅ 수정: test_claude_api → test_claude_connection
            test_result = self.chat_service.test_claude_connection()
            
            if test_result.get('status') == 'success':
                return self.success_response(
                    data=test_result,
                    message="Claude API 연결 성공"
                )
            else:
                return self.error_response(
                    message="Claude API 연결 실패",
                    details=test_result.get('message'),
                    status=503
                )
                
        except Exception as e:
            return self.error_response(
                message="Claude API 테스트 실패",
                details=str(e),
                status=500
            )
    
    # =========================
    # Multiple Chains API
    # =========================
    
    def summarize_note_endpoint(self):
        """노트 요약 API"""
        self.log_request("summarize_note")
        
        if not CHAINS_AVAILABLE:
            return self.error_response(
                message="Multiple Chains 사용 불가",
                details="specialized_chains 모듈을 확인하세요",
                status=503
            )
        
        data, error = self.get_json_data()
        if error:
            return error
        
        try:
            # 노트 ID가 제공된 경우 DB에서 조회
            if 'note_id' in data:
                note = self.note_service.get_note_by_id(data['note_id'])
                content = note.content
                context = f"제목: {note.title}"
            else:
                # 직접 컨텐츠가 제공된 경우
                content = data.get('content', '')
                context = data.get('context', '')
            
            if not content.strip():
                return self.validation_error("content", "요약할 내용이 없습니다")
            
            # 요약 실행
            result = summarize_note(content, context)
            
            if result.get('success'):
                return self.success_response(
                    data=result,
                    message="노트 요약 완료"
                )
            else:
                return self.error_response(
                    message="노트 요약 실패",
                    details=result.get('error'),
                    status=500
                )
                
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="요약 처리 실패",
                details=str(e),
                status=500
            )
    
    def analyze_note_endpoint(self):
        """노트 분석 API"""
        self.log_request("analyze_note")
        
        if not CHAINS_AVAILABLE:
            return self.error_response(
                message="Multiple Chains 사용 불가",
                details="specialized_chains 모듈을 확인하세요",
                status=503
            )
        
        data, error = self.get_json_data()
        if error:
            return error
        
        try:
            # 노트 조회 로직
            if 'note_id' in data:
                note = self.note_service.get_note_by_id(data['note_id'])
                content = note.content
                context = f"제목: {note.title}"
            else:
                content = data.get('content', '')
                context = data.get('context', '')
            
            if not content.strip():
                return self.validation_error("content", "분석할 내용이 없습니다")
            
            # 분석 실행
            result = analyze_note(content, context)
            
            if result.get('success'):
                return self.success_response(
                    data=result,
                    message="노트 분석 완료"
                )
            else:
                return self.error_response(
                    message="노트 분석 실패",
                    details=result.get('error'),
                    status=500
                )
                
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="분석 처리 실패",
                details=str(e),
                status=500
            )
    
    def recommend_notes_endpoint(self):
        """관련 노트 추천 API"""
        self.log_request("recommend_notes")
        
        if not CHAINS_AVAILABLE:
            return self.error_response(
                message="Multiple Chains 사용 불가",
                details="specialized_chains 모듈을 확인하세요",
                status=503
            )
        
        data, error = self.get_json_data()
        if error:
            return error
        
        try:
            # 현재 노트 내용 확인
            if 'note_id' in data:
                current_note_obj = self.note_service.get_note_by_id(data['note_id'])
                current_note = f"제목: {current_note_obj.title}\n\n{current_note_obj.content}"
            else:
                current_note = data.get('content', '')
            
            if not current_note.strip():
                return self.validation_error("content", "기준이 될 노트 내용이 없습니다")
            
            # 기존 노트들 조회
            limit = data.get('limit', 10)
            existing_notes = self.note_service.get_all_notes(limit=limit)
            existing_notes_data = [
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content
                }
                for note in existing_notes
            ]
            
            # 추천 실행
            result = recommend_notes(current_note, existing_notes_data)
            
            if result.get('success'):
                result['existing_notes_count'] = len(existing_notes_data)
                
                return self.success_response(
                    data=result,
                    message="관련 노트 추천 완료"
                )
            else:
                return self.error_response(
                    message="노트 추천 실패",
                    details=result.get('error'),
                    status=500
                )
                
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="추천 처리 실패",
                details=str(e),
                status=500
            )
    
    def improve_note_endpoint(self):
        """노트 개선 제안 API"""
        self.log_request("improve_note")
        
        if not CHAINS_AVAILABLE:
            return self.error_response(
                message="Multiple Chains 사용 불가",
                details="specialized_chains 모듈을 확인하세요",
                status=503
            )
        
        data, error = self.get_json_data()
        if error:
            return error
        
        try:
            # 노트 조회 로직
            if 'note_id' in data:
                note = self.note_service.get_note_by_id(data['note_id'])
                content = note.content
                context = f"제목: {note.title}"
            else:
                content = data.get('content', '')
                context = data.get('context', '')
            
            if not content.strip():
                return self.validation_error("content", "개선할 내용이 없습니다")
            
            improvement_type = data.get('improvement_type', 'suggestion')
            
            # 개선 타입에 따른 처리
            if improvement_type == 'rewrite':
                # 노트 재작성
                improvement_chain = chain_manager.get_chain('improvement')
                if not improvement_chain:
                    return self.error_response("ImprovementChain 사용 불가")
                
                style = data.get('style', 'detailed')
                result = improvement_chain.rewrite_note(content, style)
            else:
                # 개선 제안 (기본값)
                result = improve_note(content, context)
            
            if result.get('success'):
                return self.success_response(
                    data=result,
                    message=f"노트 {'재작성' if improvement_type == 'rewrite' else '개선 제안'} 완료"
                )
            else:
                return self.error_response(
                    message="노트 개선 실패",
                    details=result.get('error'),
                    status=500
                )
                
        except ValueError as e:
            return self.not_found_error("노트")
        except Exception as e:
            return self.error_response(
                message="개선 처리 실패",
                details=str(e),
                status=500
            )
    
    def get_knowledge_gaps(self):
        """지식 공백 분석 API - GET 요청 최적화"""
        self.log_request("knowledge_gaps")
        
        if not CHAINS_AVAILABLE:
            return self.error_response(
                message="Multiple Chains 사용 불가",
                status=503
            )
        
        try:
            # ✅ 수정: GET 요청이므로 JSON 파싱 제거
            # 모든 노트 조회
            notes = self.note_service.get_all_notes()
            notes_data = [
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content
                }
                for note in notes
            ]
            
            if not notes_data:
                return self.error_response(
                    message="분석할 노트가 없습니다",
                    status=400
                )
            
            # 지식 공백 분석
            analysis_chain = chain_manager.get_chain('analysis')
            if not analysis_chain:
                return self.error_response("AnalysisChain 사용 불가")
            
            result = analysis_chain.get_knowledge_gaps(notes_data)
            
            if result.get('success'):
                return self.success_response(
                    data=result,
                    message="지식 공백 분석 완료"
                )
            else:
                return self.error_response(
                    message="지식 공백 분석 실패",
                    details=result.get('error'),
                    status=500
                )
                
        except Exception as e:
            return self.error_response(
                message="지식 공백 분석 처리 실패",
                details=str(e),
                status=500
            )
    
    def get_chains_info(self):
        """사용 가능한 체인 정보 API - GET 요청 최적화"""
        self.log_request("chains_info")
        
        try:
            # ✅ 수정: GET 요청이므로 JSON 파싱 제거
            if CHAINS_AVAILABLE:
                chains_info = chain_manager.get_chains_info()
                
                # ✅ 수정: 올바른 엔드포인트 경로 설정
                chains_info['endpoints'] = {
                    'summarize': '/api/summarize',
                    'analyze': '/api/analyze',
                    'recommend': '/api/recommend',
                    'improve': '/api/improve',
                    'knowledge_gaps': '/api/knowledge-gaps'
                }
                
                return self.success_response(
                    data=chains_info,
                    message="체인 정보 조회 완료"
                )
            else:
                return self.success_response(
                    data={
                        "available": False,
                        "error": "Multiple Chains 모듈이 설치되지 않았습니다"
                    },
                    message="체인 정보 조회 (사용 불가)"
                )
                
        except Exception as e:
            return self.error_response(
                message="체인 정보 조회 실패",
                details=str(e),
                status=500
            )
    
    # =========================
    # RAG 시스템 기능들 (수정됨)
    # =========================
    
    def get_rag_status(self):
        """RAG 시스템 상태 확인 - GET 요청 최적화"""
        self.log_request("rag_status")
        
        try:
            # ✅ 수정: GET 요청이므로 JSON 파싱 제거
            status = self.chat_service.get_rag_status()
            return self.success_response(
                data={"rag_status": status},
                message="RAG 상태 조회 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="RAG 상태 조회 실패",
                details=str(e),
                status=500
            )
    
    def rebuild_rag_index(self):
        """RAG 인덱스 재구축"""
        self.log_request("rebuild_rag_index")
        
        try:
            result = self.chat_service.rebuild_rag_index()
            
            if result.get('status') == 'success':
                return self.success_response(
                    data=result,
                    message="RAG 인덱스 재구축 완료"
                )
            else:
                return self.error_response(
                    message="RAG 인덱스 재구축 실패",
                    details=result.get('message'),
                    status=500
                )
                
        except Exception as e:
            return self.error_response(
                message="RAG 인덱스 재구축 처리 실패",
                details=str(e),
                status=500
            )
    
    # =========================
    # 채팅 히스토리 기능들 (완전 구현)
    # =========================
    
    def get_chat_history(self):
        """채팅 히스토리 조회 - GET 요청 최적화"""
        self.log_request("chat_history")
        
        try:
            # ✅ 수정: GET 요청에서 쿼리 파라미터 사용
            limit = request.args.get('limit', 50, type=int)
            history = self.chat_service.get_chat_history(limit=limit)
            
            return self.success_response(
                data={"history": history},
                message=f"{len(history)}개의 채팅 기록을 조회했습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 히스토리 조회 실패",
                details=str(e),
                status=500
            )
    
    def clear_chat_history(self):
        """채팅 히스토리 삭제 - 실제 구현"""
        self.log_request("clear_chat_history")
        
        try:
            # ✅ 실제 구현된 메서드 호출
            result = self.chat_service.clear_chat_history()
            
            return self.success_response(
                data={"cleared_count": result},
                message="채팅 히스토리가 삭제되었습니다"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 히스토리 삭제 실패",
                details=str(e),
                status=500
            )
    
    def search_chat_history_endpoint(self):
        """✅ 채팅 히스토리 검색 API (새로 구현)"""
        self.log_request("search_chat_history")
        
        data, error = self.get_json_data(required_fields=['query'])
        if error:
            return error
        
        try:
            query = data['query']
            limit = data.get('limit', 10)
            
            results = self.chat_service.search_chat_history(query, limit)
            
            return self.success_response(
                data={
                    "search_results": results,
                    "query": query,
                    "total_found": len(results)
                },
                message=f"'{query}' 검색 완료: {len(results)}개 결과"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 히스토리 검색 실패",
                details=str(e),
                status=500
            )
    
    def export_chat_history_endpoint(self):
        """✅ 채팅 히스토리 내보내기 API (새로 구현)"""
        self.log_request("export_chat_history")
        
        data, error = self.get_json_data()
        if error:
            return error
        
        try:
            start_date = data.get('start_date')
            end_date = data.get('end_date')
            
            result = self.chat_service.export_chat_history(start_date, end_date)
            
            if result.get('success'):
                return self.success_response(
                    data=result['data'],
                    message=result['message']
                )
            else:
                return self.error_response(
                    message="내보내기 실패",
                    details=result.get('error'),
                    status=500
                )
            
        except Exception as e:
            return self.error_response(
                message="채팅 히스토리 내보내기 실패",
                details=str(e),
                status=500
            )
    
    def get_chat_summary_endpoint(self):
        """✅ 채팅 요약 통계 API (새로 구현)"""
        self.log_request("chat_summary")
        
        try:
            days = request.args.get('days', 7, type=int)
            
            summary = self.chat_service.get_chat_summary(days)
            
            return self.success_response(
                data=summary,
                message=f"최근 {days}일 채팅 요약 조회 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 요약 통계 실패",
                details=str(e),
                status=500
            )
    
    # =========================
    # 통계 기능들 (완전 구현)
    # =========================
    
    def get_chat_stats(self):
        """채팅 통계 정보 - GET 요청 최적화"""
        self.log_request("chat_stats")
        
        try:
            # ✅ 실제 구현된 메서드 호출
            stats = self.chat_service.get_chat_stats()
            
            # Multiple Chains 정보도 포함
            if CHAINS_AVAILABLE:
                stats['multiple_chains'] = chain_manager.get_chains_info()
            
            return self.success_response(
                data=stats,
                message="채팅 통계 조회 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="채팅 통계 조회 실패",
                details=str(e),
                status=500
            )
    
    def get_advanced_stats_endpoint(self):
        """✅ 고급 채팅 통계 API (새로 구현)"""
        self.log_request("advanced_stats")
        
        try:
            # 기본 통계
            basic_stats = self.chat_service.get_chat_stats()
            
            # 요약 통계 (여러 기간)
            summaries = {}
            for days in [1, 7, 30]:
                summaries[f"{days}d"] = self.chat_service.get_chat_summary(days)
            
            # RAG 통계
            rag_status = self.chat_service.get_rag_status()
            
            # Multiple Chains 통계
            chains_info = {}
            try:
                from chains.specialized_chains import chain_manager
                chains_info = chain_manager.get_chains_info()
            except:
                chains_info = {"available": False}
            
            from datetime import datetime
            
            advanced_stats = {
                "basic_stats": basic_stats,
                "period_summaries": summaries,
                "rag_status": rag_status,
                "chains_info": chains_info,
                "generated_at": datetime.now().isoformat()
            }
            
            return self.success_response(
                data=advanced_stats,
                message="고급 채팅 통계 조회 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="고급 통계 조회 실패",
                details=str(e),
                status=500
            )
    
    # =========================
    # 개발자 도구 (새로 구현)
    # =========================
    
    def get_debug_info_endpoint(self):
        """✅ 디버깅 정보 API (새로 구현)"""
        self.log_request("debug_info")
        
        try:
            debug_data = {
                "chat_service_methods": [
                    method for method in dir(self.chat_service) 
                    if not method.startswith('_')
                ],
                "available_chains": [],
                "system_status": {
                    "claude_api": bool(self.chat_service.api_key),
                    "rag_system": False,
                    "chains_system": False
                }
            }
            
            # RAG 상태
            try:
                rag_status = self.chat_service.get_rag_status()
                debug_data["system_status"]["rag_system"] = rag_status.get("rag_status", {}).get("available", False)
            except:
                pass
            
            # Chains 상태
            try:
                from chains.specialized_chains import chain_manager
                debug_data["available_chains"] = chain_manager.get_available_chains()
                debug_data["system_status"]["chains_system"] = len(debug_data["available_chains"]) > 0
            except:
                pass
            
            return self.success_response(
                data=debug_data,
                message="디버깅 정보 조회 완료"
            )
            
        except Exception as e:
            return self.error_response(
                message="디버깅 정보 조회 실패",
                details=str(e),
                status=500
            )