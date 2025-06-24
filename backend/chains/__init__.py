# chains/__init__.py
"""
LangChain 체인들

과제 핵심: RAG (Retrieval-Augmented Generation) 시스템
"""

# RAG 시스템 가용성 확인
try:
    from .rag_chain import rag_chain, RAG_AVAILABLE
    
    if RAG_AVAILABLE and rag_chain.is_available():
        stats = rag_chain.get_stats()
        print("✅ LangChain RAG 시스템 로드 완료")
        print(f"   - 벡터 개수: {stats['vector_count']}개")
        print(f"   - 인덱싱된 노트: {stats['indexed_notes']}개")
        print(f"   - 모델: {stats['model_name']}")
    else:
        print("⚠️ RAG 패키지 없음 - pip install faiss-cpu sentence-transformers")
        
except ImportError as e:
    print(f"⚠️ RAG 체인 임포트 실패: {e}")
    print("💡 설치 명령어: pip install faiss-cpu sentence-transformers numpy")
    rag_chain = None
    RAG_AVAILABLE = False

# 체인 가용성 확인 함수
def check_rag_availability():
    """RAG 시스템 사용 가능 여부 반환"""
    try:
        return rag_chain.is_available() if rag_chain else False
    except:
        return False

# 체인 통계 정보
def get_chains_info():
    """설치된 체인들의 정보 반환"""
    info = {
        "available_chains": [],
        "total_chains": 0,
        "rag_system": {
            "available": check_rag_availability(),
            "stats": {}
        }
    }
    
    if check_rag_availability():
        info["available_chains"].append("RAG Chain")
        info["rag_system"]["stats"] = rag_chain.get_stats()
    
    info["total_chains"] = len(info["available_chains"])
    
    return info

__all__ = [
    'rag_chain',
    'RAG_AVAILABLE', 
    'check_rag_availability',
    'get_chains_info'
]