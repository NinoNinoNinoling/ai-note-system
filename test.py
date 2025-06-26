# rag_rebuild.py - RAG 인덱스 재구축 스크립트

import requests
import json
import time
from datetime import datetime

# 서버 설정
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def print_banner():
    """시작 배너 출력"""
    print("\n" + "="*60)
    print("🔄 RAG 인덱스 재구축 스크립트")
    print("="*60)
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

def check_server_status():
    """서버 상태 확인"""
    try:
        print("🔍 Step 1: 서버 상태 확인 중...")
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        
        if response.status_code == 200:
            print("✅ 백엔드 서버: 정상 작동")
            data = response.json()
            print(f"   - 상태: {data.get('status', 'unknown')}")
            print(f"   - 데이터베이스: {data.get('database', 'unknown')}")
            return True
        else:
            print(f"❌ 서버 응답 오류: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 서버 연결 실패: localhost:5000에 백엔드가 실행 중인지 확인하세요")
        return False
    except Exception as e:
        print(f"❌ 서버 확인 오류: {str(e)}")
        return False

def check_rag_status():
    """RAG 시스템 상태 확인"""
    try:
        print("\n🔍 Step 2: RAG 시스템 상태 확인 중...")
        response = requests.get(f"{API_BASE}/rag/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ RAG 시스템 상태:")
            
            if 'data' in data:
                rag_data = data['data']
                print(f"   - 사용 가능: {rag_data.get('rag_status', {}).get('available', 'unknown')}")
                print(f"   - 총 노트 수: {rag_data.get('total_notes', 'unknown')}")
                print(f"   - 인덱스된 노트: {rag_data.get('indexed_notes', 'unknown')}")
                
                if 'vector_info' in rag_data:
                    vector_info = rag_data['vector_info']
                    print(f"   - 벡터 차원: {vector_info.get('dimension', 'unknown')}")
                    print(f"   - 인덱스 크기: {vector_info.get('index_size', 'unknown')}")
            
            return True
        else:
            print(f"❌ RAG 상태 확인 실패: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ RAG 상태 확인 오류: {str(e)}")
        return False

def rebuild_rag_index():
    """RAG 인덱스 재구축 실행"""
    try:
        print("\n🚀 Step 3: RAG 인덱스 재구축 시작...")
        print("   ⚠️  이 과정은 시간이 걸릴 수 있습니다...")
        
        start_time = time.time()
        
        response = requests.post(
            f"{API_BASE}/rag/rebuild", 
            headers={'Content-Type': 'application/json'},
            timeout=300  # 5분 타임아웃
        )
        
        end_time = time.time()
        duration = end_time - start_time
        
        if response.status_code == 200:
            print(f"✅ RAG 인덱스 재구축 완료! ({duration:.2f}초 소요)")
            
            data = response.json()
            if 'data' in data:
                result_data = data['data']
                print(f"   - 처리된 노트: {result_data.get('processed_notes', 'unknown')}개")
                print(f"   - 벡터화된 노트: {result_data.get('vectorized_notes', 'unknown')}개")
                print(f"   - 인덱스 크기: {result_data.get('index_size', 'unknown')}")
            
            print(f"   - 메시지: {data.get('message', 'No message')}")
            return True
            
        else:
            print(f"❌ RAG 인덱스 재구축 실패: {response.status_code}")
            print(f"   - 응답: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ 타임아웃: 재구축 작업이 너무 오래 걸립니다")
        return False
    except Exception as e:
        print(f"❌ RAG 재구축 오류: {str(e)}")
        return False

def test_rag_search():
    """재구축 후 RAG 검색 테스트"""
    try:
        print("\n🧪 Step 4: RAG 검색 테스트 중...")
        
        test_queries = [
            "Vue.js에 대해 알려줘",
            "AI 프로젝트에 대해 설명해줘",
            "데이터베이스 설계 방법은?"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   테스트 {i}: '{query}'")
            
            response = requests.post(
                f"{API_BASE}/rag",
                headers={'Content-Type': 'application/json'},
                json={'message': query},
                timeout=30
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data.get('data', {}).get('response', 'No response')
                
                # 응답 미리보기 (처음 100자)
                preview = ai_response[:100] + "..." if len(ai_response) > 100 else ai_response
                print(f"   ✅ 응답: {preview}")
                
                # 의미있는 답변인지 간단 체크
                meaningful_keywords = ['vue', 'ai', 'database', 'project', '노트', '프로젝트']
                if any(keyword in ai_response.lower() for keyword in meaningful_keywords):
                    print("   📝 의미있는 답변이 생성되었습니다!")
                else:
                    print("   ⚠️  일반적인 답변이 생성되었습니다.")
            else:
                print(f"   ❌ 테스트 실패: {response.status_code}")
        
        return True
        
    except Exception as e:
        print(f"❌ RAG 테스트 오류: {str(e)}")
        return False

def main():
    """메인 실행 함수"""
    print_banner()
    
    # Step 1: 서버 상태 확인
    if not check_server_status():
        print("\n❌ 서버가 실행되지 않았습니다. backend/run.py를 먼저 실행하세요.")
        return
    
    # Step 2: RAG 상태 확인
    check_rag_status()  # 실패해도 계속 진행
    
    # Step 3: 사용자 확인
    print(f"\n{'='*60}")
    confirm = input("RAG 인덱스를 재구축하시겠습니까? (y/N): ")
    if confirm.lower() not in ['y', 'yes']:
        print("❌ 작업이 취소되었습니다.")
        return
    
    # Step 4: RAG 인덱스 재구축
    if rebuild_rag_index():
        print("\n🎉 RAG 인덱스 재구축이 성공적으로 완료되었습니다!")
        
        # Step 5: 테스트 실행
        test_confirm = input("\nRAG 검색 테스트를 실행하시겠습니까? (y/N): ")
        if test_confirm.lower() in ['y', 'yes']:
            test_rag_search()
    else:
        print("\n❌ RAG 인덱스 재구축에 실패했습니다.")
    
    # 완료 메시지
    print(f"\n{'='*60}")
    print("🏁 RAG 인덱스 재구축 스크립트 완료")
    print(f"⏰ 완료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    if rebuild_rag_index:
        print("\n💡 이제 프론트엔드에서 다음과 같은 질문을 해보세요:")
        print("   - '내 노트들에서 가장 많이 다룬 주제는 뭐야?'")
        print("   - 'Vue.js에 대해 배운 내용을 정리해줘'")
        print("   - 'AI 프로젝트 계획에 대해 알려줘'")
        print("   - '데이터베이스 설계할 때 주의사항은?'")

if __name__ == "__main__":
    main()