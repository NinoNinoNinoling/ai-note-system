# backend/chains/rag_chain.py
import os
import json
import numpy as np
from typing import List, Dict, Optional
from config.settings import Config

try:
    import faiss
    from sentence_transformers import SentenceTransformer
    RAG_AVAILABLE = True
except ImportError:
    RAG_AVAILABLE = False
    print("⚠️ RAG 패키지 (faiss, sentence-transformers)가 설치되지 않았습니다")

class RAGChain:
    """Retrieval-Augmented Generation 시스템"""
    
    def __init__(self):
        self.available = RAG_AVAILABLE
        
        if not self.available:
            return
            
        try:
            # 다국어 지원 임베딩 모델
            self.model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
            self.dimension = 384  # 모델의 벡터 차원
            
            # FAISS 인덱스 초기화
            self.index = faiss.IndexFlatIP(self.dimension)  # 코사인 유사도
            self.notes_data = []  # 노트 메타데이터 저장
            
            # 파일 경로 설정
            self.index_file = Config.RAG_INDEX_PATH
            self.metadata_file = Config.RAG_METADATA_PATH
            
            # 기존 인덱스 로드
            self.load_index()
            
            print("✅ RAG 시스템 초기화 완료")
            
        except Exception as e:
            print(f"❌ RAG 시스템 초기화 실패: {e}")
            self.available = False
    
    def is_available(self) -> bool:
        """RAG 시스템 사용 가능 여부"""
        return self.available
    
    def add_note(self, note_id: int, title: str, content: str) -> bool:
        """노트를 벡터화해서 인덱스에 추가"""
        if not self.available:
            return False
            
        try:
            # 제목과 내용 합쳐서 임베딩
            text = f"제목: {title}\n\n{content}"
            
            # 벡터화
            embedding = self.model.encode([text])
            embedding = embedding / np.linalg.norm(embedding)  # 정규화
            
            # FAISS 인덱스에 추가
            self.index.add(embedding.astype('float32'))
            
            # 메타데이터 저장
            self.notes_data.append({
                "note_id": note_id,
                "title": title,
                "content_preview": content[:200] + "..." if len(content) > 200 else content,
                "full_content": content,
                "content_length": len(content)
            })
            
            # 저장
            self.save_index()
            print(f"✅ 노트 {note_id} 벡터화 완료")
            return True
            
        except Exception as e:
            print(f"❌ 노트 벡터화 오류: {e}")
            return False
    
    def search_similar_notes(self, query: str, k: int = 5) -> List[Dict]:
        """쿼리와 유사한 노트 검색"""
        if not self.available or self.index.ntotal == 0:
            return []
            
        try:
            # 쿼리 벡터화
            query_embedding = self.model.encode([query])
            query_embedding = query_embedding / np.linalg.norm(query_embedding)
            
            # 유사한 벡터 검색
            scores, indices = self.index.search(query_embedding.astype('float32'), min(k, self.index.ntotal))
            
            results = []
            for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
                if 0 <= idx < len(self.notes_data):
                    note = self.notes_data[idx].copy()
                    note['similarity_score'] = float(score)
                    note['rank'] = i + 1
                    results.append(note)
            
            return results
            
        except Exception as e:
            print(f"❌ 유사 노트 검색 오류: {e}")
            return []
    
    def get_context_for_query(self, query: str, k: int = 3) -> str:
        """쿼리에 대한 컨텍스트 생성 (AI 모델에 전달용)"""
        similar_notes = self.search_similar_notes(query, k)
        
        if not similar_notes:
            return "관련된 노트를 찾을 수 없습니다."
        
        context_parts = ["다음은 관련된 노트들입니다:\n"]
        
        for i, note in enumerate(similar_notes, 1):
            context_parts.append(f"[노트 {i}] {note['title']}")
            context_parts.append(f"내용: {note['full_content']}")
            context_parts.append(f"유사도: {note['similarity_score']:.3f}\n")
        
        return "\n".join(context_parts)
    
    def save_index(self) -> bool:
        """인덱스와 메타데이터 저장"""
        if not self.available:
            return False
            
        try:
            # FAISS 인덱스 저장
            if self.index.ntotal > 0:
                faiss.write_index(self.index, self.index_file)
            
            # 메타데이터 저장
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self.notes_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 저장 오류: {e}")
            return False
    
    def load_index(self) -> bool:
        """기존 인덱스와 메타데이터 로드"""
        if not self.available:
            return False
            
        try:
            # FAISS 인덱스 로드
            if os.path.exists(self.index_file):
                self.index = faiss.read_index(self.index_file)
                print(f"✅ 기존 FAISS 인덱스 로드 완료 ({self.index.ntotal}개 벡터)")
            
            # 메타데이터 로드
            if os.path.exists(self.metadata_file):
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self.notes_data = json.load(f)
                print(f"✅ 메타데이터 로드 완료 ({len(self.notes_data)}개 노트)")
            
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 로드 오류: {e}")
            return False
    
    def rebuild_index(self, notes: List[Dict]) -> bool:
        """전체 인덱스 재구축"""
        if not self.available:
            return False
            
        print("🔄 RAG 인덱스 재구축 시작...")
        
        try:
            # 기존 인덱스 초기화
            self.index = faiss.IndexFlatIP(self.dimension)
            self.notes_data = []
            
            # 모든 노트 다시 추가
            success_count = 0
            for note in notes:
                if self.add_note(note['id'], note['title'], note['content']):
                    success_count += 1
            
            print(f"✅ RAG 인덱스 재구축 완료! ({success_count}/{len(notes)}개 성공)")
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 재구축 오류: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """RAG 시스템 통계 정보"""
        return {
            "available": self.available,
            "indexed_notes": len(self.notes_data),
            "vector_count": self.index.ntotal if self.available else 0,
            "model_name": "paraphrase-multilingual-MiniLM-L12-v2" if self.available else None,
            "dimension": self.dimension if self.available else None
        }
    
    def clear_index(self) -> bool:
        """인덱스 완전 삭제"""
        if not self.available:
            return False
            
        try:
            # 메모리상 인덱스 초기화
            self.index = faiss.IndexFlatIP(self.dimension)
            self.notes_data = []
            
            # 파일 삭제
            if os.path.exists(self.index_file):
                os.remove(self.index_file)
            if os.path.exists(self.metadata_file):
                os.remove(self.metadata_file)
            
            print("✅ RAG 인덱스 완전 삭제 완료")
            return True
            
        except Exception as e:
            print(f"❌ 인덱스 삭제 오류: {e}")
            return False

# 전역 RAG 체인 인스턴스
rag_chain = RAGChain()