# backend/app/routes/chat.py
"""
완전한 Chat Routes - 모든 기능 포함

새로 추가된 엔드포인트들:
- 채팅 히스토리 검색, 내보내기, 요약
- 고급 통계 및 디버깅 정보
- 모든 Multiple Chains API
- 체인 관리 및 테스트 기능
"""

from flask import Blueprint, request
from app.controllers.chat_controller import ChatController

# Blueprint 생성
chat_bp = Blueprint('chat', __name__)

# Controller 인스턴스 생성
controller = ChatController()


# ====== 기본 채팅 기능 ======

@chat_bp.route('/', methods=['POST'])
def chat():
    """기본 AI 채팅"""
    return controller.basic_chat()


@chat_bp.route('/test', methods=['GET'])
def test_claude():
    """Claude API 연결 테스트"""
    return controller.test_claude_connection()


# ====== RAG 기반 채팅 ======

@chat_bp.route('/rag', methods=['POST'])
def chat_with_rag():
    """RAG 기반 지능형 채팅"""
    return controller.rag_chat()


@chat_bp.route('/rag/status', methods=['GET'])
def rag_status():
    """RAG 시스템 상태 확인"""
    return controller.get_rag_status()


@chat_bp.route('/rag/rebuild', methods=['POST'])
def rebuild_rag_index():
    """RAG 인덱스 재구축"""
    return controller.rebuild_rag_index()


# ====== Multiple Chains API ======

@chat_bp.route('/summarize', methods=['POST'])
def summarize_note():
    """노트 요약 API"""
    return controller.summarize_note_endpoint()


@chat_bp.route('/analyze', methods=['POST'])
def analyze_note():
    """노트 분석 API"""
    return controller.analyze_note_endpoint()


@chat_bp.route('/recommend', methods=['POST'])
def recommend_notes():
    """관련 노트 추천 API"""
    return controller.recommend_notes_endpoint()


@chat_bp.route('/improve', methods=['POST'])
def improve_note():
    """노트 개선 제안 API"""
    return controller.improve_note_endpoint()


@chat_bp.route('/knowledge-gaps', methods=['GET'])
def knowledge_gaps():
    """지식 공백 분석 API"""
    return controller.get_knowledge_gaps()


@chat_bp.route('/chains', methods=['GET'])
def chains_info():
    """사용 가능한 체인 정보 API"""
    return controller.get_chains_info()


# ====== 일괄 처리 API ======

@chat_bp.route('/batch/summarize', methods=['POST'])
def batch_summarize():
    """여러 노트 일괄 요약"""
    data, error = controller.get_json_data()
    if error:
        return error
    
    try:
        from chains.specialized_chains import chain_manager
        
        summarization_chain = chain_manager.get_chain('summarization')
        if not summarization_chain or not summarization_chain.is_available():
            return controller.error_response(
                message="SummarizationChain 사용 불가",
                status=503
            )
        
        # 노트 조회
        note_ids = data.get('note_ids', [])
        limit = data.get('limit', 10)
        
        if note_ids:
            notes = []
            for note_id in note_ids[:limit]:
                try:
                    note = controller.note_service.get_note_by_id(note_id)
                    notes.append({
                        "id": note.id,
                        "title": note.title,
                        "content": note.content
                    })
                except:
                    continue
        else:
            all_notes = controller.note_service.get_all_notes(limit=limit)
            notes = [
                {
                    "id": note.id,
                    "title": note.title,
                    "content": note.content
                }
                for note in all_notes
            ]
        
        if not notes:
            return controller.error_response(
                message="요약할 노트가 없습니다",
                status=400
            )
        
        # 일괄 요약 실행
        result = summarization_chain.summarize_multiple_notes(notes)
        
        if result.get('success'):
            return controller.success_response(
                data=result,
                message=f"{result['summarized_notes']}개 노트 일괄 요약 완료"
            )
        else:
            return controller.error_response(
                message="일괄 요약 실패",
                details=result.get('error'),
                status=500
            )
            
    except Exception as e:
        return controller.error_response(
            message="일괄 요약 처리 실패",
            details=str(e),
            status=500
        )


# ====== 체인 관리 ======

@chat_bp.route('/chains/status', methods=['GET'])
def chains_status():
    """각 체인별 상세 상태 확인"""
    try:
        from chains.specialized_chains import chain_manager, CHAINS_AVAILABLE
        
        if not CHAINS_AVAILABLE:
            return controller.success_response(
                data={
                    "available": False,
                    "error": "specialized_chains 모듈 없음"
                },
                message="Multiple Chains 사용 불가"
            )
        
        status_details = {}
        
        for chain_name in ['summarization', 'analysis', 'recommendation', 'improvement']:
            chain = chain_manager.get_chain(chain_name)
            status_details[chain_name] = {
                "available": chain.is_available() if chain else False,
                "loaded": chain is not None,
                "error": None if chain and chain.is_available() else "체인 로드 실패"
            }
        
        overall_info = chain_manager.get_chains_info()
        overall_info['chain_details'] = status_details
        
        return controller.success_response(
            data=overall_info,
            message="체인 상태 조회 완료"
        )
        
    except Exception as e:
        return controller.error_response(
            message="체인 상태 조회 실패",
            details=str(e),
            status=500
        )


@chat_bp.route('/chains/test', methods=['POST'])
def test_chains():
    """모든 체인 기능 테스트"""
    try:
        from chains.specialized_chains import chain_manager, CHAINS_AVAILABLE
        
        if not CHAINS_AVAILABLE:
            return controller.error_response(
                message="Multiple Chains 사용 불가",
                status=503
            )
        
        data = request.get_json() or {}
        test_content = data.get('test_content', """
# 테스트 노트

## Vue.js 학습 내용
- Composition API
- ref(), reactive()
- computed 속성

## 다음 학습 계획
- Vue Router
- Pinia 상태 관리
""")
        
        test_results = {}
        
        # 각 체인별 테스트
        if chain_manager.is_available('summarization'):
            from chains.specialized_chains import summarize_note
            result = summarize_note(test_content, "테스트 컨텍스트")
            test_results['summarization'] = {
                "success": result.get('success', False),
                "output_length": len(result.get('summary', '')) if result.get('success') else 0
            }
        
        if chain_manager.is_available('analysis'):
            from chains.specialized_chains import analyze_note
            result = analyze_note(test_content, "테스트 컨텍스트")
            test_results['analysis'] = {
                "success": result.get('success', False),
                "output_length": len(result.get('analysis', '')) if result.get('success') else 0
            }
        
        if chain_manager.is_available('improvement'):
            from chains.specialized_chains import improve_note
            result = improve_note(test_content, "테스트 컨텍스트")
            test_results['improvement'] = {
                "success": result.get('success', False),
                "output_length": len(result.get('improvements', '')) if result.get('success') else 0
            }
        
        if chain_manager.is_available('recommendation'):
            dummy_notes = [
                {"id": 1, "title": "React 기초", "content": "React는 UI 라이브러리입니다"},
                {"id": 2, "title": "JavaScript ES6", "content": "ES6의 새로운 기능들"}
            ]
            from chains.specialized_chains import recommend_notes
            result = recommend_notes(test_content, dummy_notes)
            test_results['recommendation'] = {
                "success": result.get('success', False),
                "output_length": len(result.get('recommendations', '')) if result.get('success') else 0
            }
        
        # 전체 테스트 결과
        total_tests = len(test_results)
        successful_tests = sum(1 for r in test_results.values() if r.get('success'))
        
        return controller.success_response(
            data={
                "test_results": test_results,
                "summary": {
                    "total_chains_tested": total_tests,
                    "successful_chains": successful_tests,
                    "success_rate": f"{successful_tests}/{total_tests}",
                    "all_passed": successful_tests == total_tests
                },
                "test_content_length": len(test_content)
            },
            message=f"체인 테스트 완료 ({successful_tests}/{total_tests} 성공)"
        )
        
    except Exception as e:
        return controller.error_response(
            message="체인 테스트 실패",
            details=str(e),
            status=500
        )


# ====== 채팅 히스토리 (확장됨) ======

@chat_bp.route('/history', methods=['GET'])
def get_chat_history():
    """채팅 히스토리 조회"""
    return controller.get_chat_history()


@chat_bp.route('/history', methods=['DELETE'])
def clear_chat_history():
    """채팅 히스토리 삭제"""
    return controller.clear_chat_history()


@chat_bp.route('/history/search', methods=['POST'])
def search_chat_history():
    """✅ 채팅 히스토리 검색 (새로 추가)"""
    return controller.search_chat_history_endpoint()


@chat_bp.route('/history/export', methods=['POST'])
def export_chat_history():
    """✅ 채팅 히스토리 내보내기 (새로 추가)"""
    return controller.export_chat_history_endpoint()


@chat_bp.route('/history/summary', methods=['GET'])
def get_chat_summary():
    """✅ 채팅 요약 통계 (새로 추가)"""
    return controller.get_chat_summary_endpoint()


# ====== 통계 및 정보 ======

@chat_bp.route('/stats', methods=['GET'])
def get_chat_stats():
    """채팅 통계 정보 (개선됨)"""
    return controller.get_chat_stats()


@chat_bp.route('/stats/advanced', methods=['GET'])
def get_advanced_stats():
    """✅ 고급 채팅 통계 (새로 추가)"""
    return controller.get_advanced_stats_endpoint()


# ====== API 정보 ======

@chat_bp.route('/endpoints', methods=['GET'])
def list_endpoints():
    """사용 가능한 모든 채팅 관련 엔드포인트 목록 (확장됨)"""
    endpoints = {
        # 기본 채팅
        "basic_chat": {
            "url": "/api/",
            "method": "POST",
            "description": "기본 AI 채팅",
            "body": {"message": "str"}
        },
        "rag_chat": {
            "url": "/api/rag", 
            "method": "POST",
            "description": "RAG 기반 지능형 채팅",
            "body": {"message": "str"}
        },
        
        # Multiple Chains
        "summarize": {
            "url": "/api/summarize",
            "method": "POST", 
            "description": "노트 요약",
            "body": {"note_id": "int or content: str"}
        },
        "analyze": {
            "url": "/api/analyze",
            "method": "POST",
            "description": "노트 분석",
            "body": {"note_id": "int or content: str"}
        },
        "recommend": {
            "url": "/api/recommend",
            "method": "POST",
            "description": "관련 노트 추천",
            "body": {"note_id": "int or content: str", "limit": "int"}
        },
        "improve": {
            "url": "/api/improve",
            "method": "POST",
            "description": "노트 개선 제안",
            "body": {"note_id": "int or content: str", "improvement_type": "str"}
        },
        
        # 일괄 처리
        "batch_summarize": {
            "url": "/api/batch/summarize",
            "method": "POST",
            "description": "일괄 요약",
            "body": {"note_ids": "[int]", "limit": "int"}
        },
        
        # 히스토리 관리
        "history": {
            "url": "/api/history",
            "method": "GET",
            "description": "채팅 히스토리 조회",
            "params": {"limit": "int"}
        },
        "history_search": {
            "url": "/api/history/search",
            "method": "POST",
            "description": "채팅 히스토리 검색",
            "body": {"query": "str", "limit": "int"}
        },
        "history_export": {
            "url": "/api/history/export",
            "method": "POST",
            "description": "채팅 히스토리 내보내기",
            "body": {"start_date": "str", "end_date": "str"}
        },
        "history_summary": {
            "url": "/api/history/summary",
            "method": "GET",
            "description": "채팅 요약 통계",
            "params": {"days": "int"}
        },
        
        # 통계 및 상태
        "stats": {
            "url": "/api/stats",
            "method": "GET",
            "description": "기본 채팅 통계"
        },
        "stats_advanced": {
            "url": "/api/stats/advanced",
            "method": "GET",
            "description": "고급 채팅 통계"
        },
        "rag_status": {
            "url": "/api/rag/status",
            "method": "GET",
            "description": "RAG 시스템 상태"
        },
        "chains_info": {
            "url": "/api/chains",
            "method": "GET", 
            "description": "체인 정보 조회"
        },
        "chains_status": {
            "url": "/api/chains/status",
            "method": "GET",
            "description": "체인 상세 상태"
        },
        "chains_test": {
            "url": "/api/chains/test",
            "method": "POST",
            "description": "체인 통합 테스트"
        }
    }
    
    return controller.success_response(
        data={
            "endpoints": endpoints,
            "total_endpoints": len(endpoints),
            "categories": {
                "basic_chat": 2,
                "multiple_chains": 4,
                "batch_processing": 1,
                "history_management": 4,
                "statistics": 2,
                "system_status": 3
            }
        },
        message="채팅 API 엔드포인트 목록 (완전 버전)"
    )


# ====== 개발자 도구 ======

@chat_bp.route('/debug/info', methods=['GET'])
def debug_info():
    """✅ 디버깅 정보 (개발용)"""
    return controller.get_debug_info_endpoint()