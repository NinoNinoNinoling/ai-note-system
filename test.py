# rag_test.py - RAG/Chat/Health API 직접 테스트
import requests
import json

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_rag_api():
    """RAG API 직접 테스트 (/api/rag)"""
    print("🧪 RAG API 직접 테스트")
    print("="*50)

    test_message = "Vue.js에 대해 알려줘"

    try:
        print(f"📤 요청 → {API_BASE}/rag : {test_message}")
        response = requests.post(
            f"{API_BASE}/rag",
            json={'message': test_message},
            timeout=30
        )

        print(f"📥 상태코드: {response.status_code}")
        if response.status_code != 200:
            print("❌ 실패:", response.text)
            return

        data = response.json().get('data', {})
        print("📥 ai_response:", data.get('ai_response'))
        print("📥 relevant_notes:", data.get('relevant_notes'))
        print("📥 relevant_notes_count:", data.get('relevant_notes_count'))
        print("📥 model:", data.get('model'))
        print("📥 timestamp:", data.get('timestamp'))

    except Exception as e:
        print("❌ RAG 테스트 실패:", e)


def test_claude_api():
    """Claude 채팅 테스트 (/api/)"""
    print("\n🤖 Claude API 직접 테스트")
    print("="*50)

    try:
        # 실제 등록된 엔드포인트는 '/api/' (base POST) 입니다.
        resp = requests.post(
            f"{API_BASE}/",
            json={'message': '안녕하세요, 간단한 테스트입니다.'},
            timeout=30
        )
        print(f"📥 상태코드: {resp.status_code}")
        if resp.status_code != 200:
            print("❌ 실패:", resp.text)
            return

        body = resp.json().get('data', {})
        print("📥 claude-response:", body.get('response'))

    except Exception as e:
        print("❌ Claude 테스트 실패:", e)


def check_environment():
    """시스템 헬스 체크 (/health)"""
    print("\n🔧 시스템 헬스 체크")
    print("="*50)

    try:
        # Main Blueprint에 등록된 /health 엔드포인트 호출
        resp = requests.get(f"{BASE_URL}/health", timeout=10)
        print(f"📥 상태코드: {resp.status_code}")
        print("📥 응답 본문:", resp.text)
    except Exception as e:
        print("❌ 헬스 체크 실패:", e)


if __name__ == "__main__":
    test_rag_api()
    test_claude_api()
    check_environment()