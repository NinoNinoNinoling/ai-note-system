# debug_error_test.py
"""
에러 처리 테스트 디버깅

빈 메시지와 필수 필드 누락 에러가 제대로 처리되는지 확인
"""

import requests
import json

BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

def test_error_case(test_name, payload):
    """개별 에러 케이스 테스트"""
    print(f"\n🧪 {test_name}")
    print(f"📤 요청 데이터: {payload}")
    
    try:
        response = requests.post(
            f"{API_BASE}/",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        print(f"📨 응답 상태: {response.status_code}")
        
        try:
            data = response.json()
            print(f"📄 응답 내용: {json.dumps(data, ensure_ascii=False, indent=2)}")
            
            # 에러 처리 여부 판단
            if response.status_code == 400:
                print("✅ HTTP 400 에러 정상 반환")
            elif not data.get("success", True):
                print("✅ success=false로 에러 처리됨")
            else:
                print("❌ 에러 처리되지 않음")
                
        except json.JSONDecodeError:
            print(f"❌ JSON 파싱 실패, 응답 텍스트: {response.text}")
            
    except Exception as e:
        print(f"❌ 요청 실패: {str(e)}")

def main():
    print("🔍 에러 처리 테스트 디버깅")
    
    # 서버 연결 확인
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print("❌ 서버에 연결할 수 없습니다")
            return
        print("✅ 서버 연결 확인")
    except:
        print("❌ 서버에 연결할 수 없습니다")
        return
    
    # 1. 빈 메시지 테스트
    test_error_case("빈 메시지 테스트", {"message": ""})
    
    # 2. 필수 필드 누락 테스트
    test_error_case("필수 필드 누락 테스트", {"not_message": "test"})
    
    # 3. 정상 메시지 테스트 (비교용)
    test_error_case("정상 메시지 테스트 (비교용)", {"message": "안녕하세요"})
    
    print("\n✅ 디버깅 완료!")

if __name__ == "__main__":
    main()