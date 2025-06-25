# test_notes_api.py
# Note API 테스트 스크립트 (윈도우 호환)

import requests
import json
import time

BASE_URL = "http://localhost:5000"

def print_section(title):
    print(f"\n{'='*50}")
    print(f"🧪 {title}")
    print('='*50)

def print_response(response, title=""):
    if title:
        print(f"\n📋 {title}")
    print(f"Status: {response.status_code}")
    try:
        data = response.json()
        print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
    except:
        print(f"Response: {response.text}")
    print("-" * 30)

def test_server_health():
    print_section("1. 서버 상태 확인")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_response(response, "헬스 체크")
        return response.status_code == 200
    except requests.exceptions.ConnectionError:
        print("❌ 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인해주세요.")
        return False

def test_note_creation():
    print_section("2. 노트 생성 테스트")
    
    # 2-1. 자동 태그 추출 노트
    note1 = {
        "title": "Vue.js 학습 노트",
        "content": "# Vue.js 기초\n\n## Composition API\n- ref(), reactive()\n- computed, watch\n\n#vue #frontend #javascript"
    }
    
    response = requests.post(f"{BASE_URL}/api/notes", json=note1)
    print_response(response, "자동 태그 추출 노트 생성")
    
    # 2-2. 명시적 태그 노트
    note2 = {
        "title": "Python Flask API",
        "content": "Flask로 REST API 만들기\n\n- Blueprint 사용\n- 에러 처리",
        "tags": ["python", "flask", "api", "backend"]
    }
    
    response = requests.post(f"{BASE_URL}/api/notes", json=note2)
    print_response(response, "명시적 태그 노트 생성")
    
    # 2-3. 검색용 노트
    note3 = {
        "title": "데이터베이스 설계",
        "content": "# 데이터베이스 설계 원칙\n\n## 정규화\n1. 1NF - 원자값\n2. 2NF - 완전 함수 종속\n3. 3NF - 이행적 종속 제거\n\n## 인덱스\n- 성능 향상\n- 메모리 사용량 증가\n\n#database #design #sql"
    }
    
    response = requests.post(f"{BASE_URL}/api/notes", json=note3)
    print_response(response, "검색용 노트 생성")

def test_note_retrieval():
    print_section("3. 노트 조회 테스트")
    
    # 3-1. 전체 노트 목록
    response = requests.get(f"{BASE_URL}/api/notes")
    print_response(response, "전체 노트 목록")
    
    # 3-2. 페이지네이션
    response = requests.get(f"{BASE_URL}/api/notes?limit=2")
    print_response(response, "페이지네이션 (limit=2)")
    
    # 3-3. 특정 노트 조회
    response = requests.get(f"{BASE_URL}/api/notes/1")
    print_response(response, "노트 ID 1 조회")
    
    # 3-4. 없는 노트 조회 (에러 테스트)
    response = requests.get(f"{BASE_URL}/api/notes/999")
    print_response(response, "없는 노트 조회 (에러 테스트)")

def test_note_update():
    print_section("4. 노트 업데이트 테스트")
    
    # 4-1. 제목만 업데이트
    update_data1 = {
        "title": "Vue.js 학습 노트 (업데이트됨)"
    }
    response = requests.put(f"{BASE_URL}/api/notes/1", json=update_data1)
    print_response(response, "제목만 업데이트")
    
    # 4-2. 내용과 태그 업데이트
    update_data2 = {
        "content": "Flask REST API 개발 가이드\n\n- Blueprint로 모듈화\n- 에러 처리 표준화\n- 로깅 시스템",
        "tags": ["python", "flask", "rest-api", "guide"]
    }
    response = requests.put(f"{BASE_URL}/api/notes/2", json=update_data2)
    print_response(response, "내용과 태그 업데이트")

def test_search_functionality():
    print_section("5. 검색 기능 테스트")
    
    # 5-1. 텍스트 검색
    search_data1 = {"query": "vue"}
    response = requests.post(f"{BASE_URL}/api/notes/search", json=search_data1)
    print_response(response, "텍스트 검색 ('vue')")
    
    # 5-2. 태그 검색
    search_data2 = {"tags": ["python"]}
    response = requests.post(f"{BASE_URL}/api/notes/search", json=search_data2)
    print_response(response, "태그 검색 (['python'])")
    
    # 5-3. 통합 검색
    search_data3 = {
        "query": "api",
        "tags": ["flask"]
    }
    response = requests.post(f"{BASE_URL}/api/notes/search", json=search_data3)
    print_response(response, "통합 검색 (텍스트: 'api', 태그: ['flask'])")
    
    # 5-4. 빈 검색 (최근 노트)
    search_data4 = {}
    response = requests.post(f"{BASE_URL}/api/notes/search", json=search_data4)
    print_response(response, "빈 검색 (최근 노트)")

def test_tag_features():
    print_section("6. 태그 관련 테스트")
    
    # 6-1. 전체 태그 목록
    response = requests.get(f"{BASE_URL}/api/notes/tags")
    print_response(response, "전체 태그 목록")
    
    # 6-2. 특정 태그의 노트들
    response = requests.get(f"{BASE_URL}/api/notes/tags/python")
    print_response(response, "'python' 태그 노트들")

def test_stats_and_utilities():
    print_section("7. 통계 및 유틸리티 테스트")
    
    # 7-1. 노트 통계
    response = requests.get(f"{BASE_URL}/api/notes/stats")
    print_response(response, "노트 통계")
    
    # 7-2. 최근 노트들
    response = requests.get(f"{BASE_URL}/api/notes/recent?limit=3")
    print_response(response, "최근 노트 (limit=3)")
    
    # 7-3. 데이터 검증
    validate_data = {
        "title": "테스트 노트",
        "content": "이것은 테스트 노트입니다.\n\n#test #validation",
        "tags": ["manual", "tag"]
    }
    response = requests.post(f"{BASE_URL}/api/notes/validate", json=validate_data)
    print_response(response, "데이터 검증 테스트")

def test_error_handling():
    print_section("8. 에러 처리 테스트")
    
    # 8-1. 빈 제목 에러
    error_data1 = {
        "title": "",
        "content": "내용은 있음"
    }
    response = requests.post(f"{BASE_URL}/api/notes", json=error_data1)
    print_response(response, "빈 제목 에러 테스트")
    
    # 8-2. 필수 필드 누락 에러
    error_data2 = {
        "title": "제목만 있음"
    }
    response = requests.post(f"{BASE_URL}/api/notes", json=error_data2)
    print_response(response, "필수 필드 누락 에러")
    
    # 8-3. 잘못된 JSON (파이썬에서는 직접 구현하기 어려우니 패스)
    print("\n📋 잘못된 JSON 에러 테스트")
    print("Status: (Python requests가 자동으로 올바른 JSON을 생성하므로 패스)")

def test_note_deletion():
    print_section("9. 삭제 테스트")
    
    # 9-1. 노트 삭제
    response = requests.delete(f"{BASE_URL}/api/notes/3")
    print_response(response, "노트 삭제 (ID 3)")
    
    # 9-2. 삭제된 노트 조회 확인
    response = requests.get(f"{BASE_URL}/api/notes/3")
    print_response(response, "삭제된 노트 조회 확인")

def main():
    print("🧪 Note API 테스트 시작...")
    print("백엔드 서버가 http://localhost:5000 에서 실행 중이어야 합니다.")
    
    # 서버 상태 확인
    if not test_server_health():
        print("\n❌ 서버 연결 실패. 테스트를 중단합니다.")
        print("\n📋 체크사항:")
        print("1. 백엔드 서버가 실행 중인가요? (python app.py)")
        print("2. 포트 5000이 사용 중인가요?")
        print("3. 방화벽이 localhost:5000을 차단하고 있나요?")
        return
    
    print("\n✅ 서버 연결 성공! 테스트를 진행합니다...\n")
    
    try:
        # 모든 테스트 실행
        test_note_creation()
        time.sleep(0.5)  # 약간의 지연
        
        test_note_retrieval()
        time.sleep(0.5)
        
        test_note_update()
        time.sleep(0.5)
        
        test_search_functionality()
        time.sleep(0.5)
        
        test_tag_features()
        time.sleep(0.5)
        
        test_stats_and_utilities()
        time.sleep(0.5)
        
        test_error_handling()
        time.sleep(0.5)
        
        test_note_deletion()
        
        print_section("테스트 완료!")
        print("✅ 모든 API 테스트가 완료되었습니다!")
        print("\n📋 결과 확인:")
        print("- 성공 응답들이 {'success': True, ...} 형태인가요?")
        print("- 에러 응답들이 {'success': False, ...} 형태인가요?")
        print("- 자동 태그 추출이 동작했나요?")
        print("- 검색 기능이 정상 동작했나요?")
        print("\n🚀 모든 기능이 정상이면 커밋하세요!")
        
    except Exception as e:
        print(f"\n❌ 테스트 중 예외 발생: {e}")
        print("상세 에러를 확인하고 코드를 수정해주세요.")

if __name__ == "__main__":
    main()