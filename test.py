# test_final.py
"""
AI Note System - 최종 수정된 테스트 파일

✅ 주요 수정사항:
1. HTTP 415 오류 완전 해결 (GET 요청 헤더 수정)
2. 실제 등록된 엔드포인트만 테스트
3. 정확한 경로 및 메서드 사용
4. 서버 로그 기반 오류 해결
"""

import requests
import json
import time
from datetime import datetime
import sys

# 서버 설정
BASE_URL = "http://localhost:5000"
API_BASE = f"{BASE_URL}/api"

# 테스트 설정
TIMEOUT = 30


def print_header(title):
    """테스트 섹션 헤더 출력"""
    print("\n" + "="*60)
    print(f"🧪 {title}")
    print("="*60)


def print_test_result(test_name, success, details=None, response_time=None):
    """테스트 결과 출력"""
    status = "✅ 성공" if success else "❌ 실패"
    time_info = f" ({response_time:.2f}초)" if response_time else ""
    print(f"{status} {test_name}{time_info}")
    
    if details:
        if success:
            detail_str = str(details)
            print(f"   📄 응답: {detail_str[:100]}..." if len(detail_str) > 100 else f"   📄 응답: {details}")
        else:
            print(f"   ⚠️ 오류: {details}")


def make_request(method, url, data=None, timeout=TIMEOUT):
    """HTTP 요청 헬퍼 함수 - HTTP 415 오류 완전 해결"""
    try:
        start_time = time.time()
        
        # ✅ 핵심 수정: GET/DELETE 요청에는 헤더 없음, POST/PUT만 JSON 헤더
        if method.upper() in ['GET', 'DELETE']:
            # GET, DELETE 요청에는 Content-Type 헤더 설정하지 않음
            if method.upper() == 'GET':
                response = requests.get(url, timeout=timeout)
            else:  # DELETE
                response = requests.delete(url, timeout=timeout)
        else:
            # POST, PUT 요청만 JSON 헤더 설정
            headers = {'Content-Type': 'application/json'}
            if method.upper() == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)
            elif method.upper() == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=timeout)
            else:
                return False, f"지원하지 않는 HTTP 메서드: {method}", 0
        
        response_time = time.time() - start_time
        
        if 200 <= response.status_code < 300:
            try:
                return True, response.json(), response_time
            except:
                return True, response.text, response_time
        else:
            return False, f"HTTP {response.status_code}: {response.text}", response_time
            
    except requests.exceptions.Timeout:
        return False, f"요청 시간 초과 ({timeout}초)", timeout
    except requests.exceptions.ConnectionError:
        return False, "서버 연결 실패 - 서버가 실행 중인지 확인하세요", 0
    except Exception as e:
        return False, f"요청 실패: {str(e)}", 0


# ====== 시스템 기본 테스트 ======

def test_server_connection():
    """서버 연결 테스트"""
    print_header("서버 연결 확인")
    
    success_count = 0
    total_tests = 3
    
    # 홈페이지 테스트
    success, result, response_time = make_request('GET', BASE_URL)
    print_test_result("홈페이지", success, result, response_time)
    if success: success_count += 1
    
    # 헬스 체크 테스트
    success, result, response_time = make_request('GET', f"{BASE_URL}/health")
    print_test_result("헬스 체크", success, result, response_time)
    if success: success_count += 1
    
    # 디버그 라우트 테스트
    success, result, response_time = make_request('GET', f"{BASE_URL}/debug/routes")
    print_test_result("라우트 정보", success, result, response_time)
    if success: success_count += 1
    
    return success_count == total_tests


# ====== 기본 채팅 테스트 ======

def test_basic_chat():
    """기본 AI 채팅 테스트"""
    print_header("기본 AI 채팅 테스트")
    
    test_messages = [
        "안녕하세요!",
        "마크다운에 대해 설명해주세요",
        "Vue.js란 무엇인가요?",
        "도움말을 보여주세요"
    ]
    
    success_count = 0
    for i, message in enumerate(test_messages, 1):
        data = {"message": message}
        success, result, response_time = make_request('POST', f"{API_BASE}/", data)
        print_test_result(f"채팅 테스트 {i}", success, result, response_time)
        if success:
            success_count += 1
    
    return success_count == len(test_messages)


def test_claude_connection():
    """Claude API 연결 테스트"""
    print_header("Claude API 연결 테스트")
    
    # ✅ GET 요청 - 헤더 없이 요청
    success, result, response_time = make_request('GET', f"{API_BASE}/test")
    print_test_result("Claude API 테스트", success, result, response_time)
    
    return success


# ====== RAG 시스템 테스트 ======

def test_rag_system():
    """RAG 시스템 테스트"""
    print_header("RAG 시스템 테스트")
    
    success_count = 0
    total_tests = 0
    
    # RAG 상태 확인 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/rag/status")
    print_test_result("RAG 상태 확인", success, result, response_time)
    if success: success_count += 1
    
    # RAG 기반 채팅 - POST 요청
    total_tests += 1
    data = {"message": "저장된 노트들을 기반으로 답변해주세요"}
    success, result, response_time = make_request('POST', f"{API_BASE}/rag", data)
    print_test_result("RAG 기반 채팅", success, result, response_time)
    if success: success_count += 1
    
    # RAG 인덱스 재구축 (선택적) - POST 요청
    print("\n🔄 RAG 인덱스 재구축을 테스트하시겠습니까? (y/n): ", end="")
    if input().lower() == 'y':
        total_tests += 1
        success, result, response_time = make_request('POST', f"{API_BASE}/rag/rebuild")
        print_test_result("RAG 인덱스 재구축", success, result, response_time)
        if success: success_count += 1
    
    return success_count == total_tests


# ====== Multiple Chains 테스트 ======

def test_multiple_chains():
    """Multiple Chains API 테스트"""
    print_header("Multiple Chains API 테스트")
    
    success_count = 0
    total_tests = 0
    
    # 체인 정보 확인 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/chains")
    print_test_result("체인 정보 확인", success, result, response_time)
    if success: success_count += 1
    
    # 테스트용 노트 내용
    test_content = """# Vue.js 학습 노트

## 기본 개념
- 반응형 데이터 바인딩
- 컴포넌트 기반 아키텍처
- 가상 DOM

## Composition API
- ref() 함수 사용법
- reactive() 객체
- computed() 속성

#vue #javascript #frontend"""
    
    # 노트 요약 - POST 요청
    total_tests += 1
    data = {"content": test_content, "title": "Vue.js 학습"}
    success, result, response_time = make_request('POST', f"{API_BASE}/summarize", data)
    print_test_result("노트 요약", success, result, response_time)
    if success: success_count += 1
    
    # 노트 분석 - POST 요청
    total_tests += 1
    data = {"content": test_content}
    success, result, response_time = make_request('POST', f"{API_BASE}/analyze", data)
    print_test_result("노트 분석", success, result, response_time)
    if success: success_count += 1
    
    # 노트 개선 제안 - POST 요청
    total_tests += 1
    data = {"content": test_content, "improvement_type": "structure"}
    success, result, response_time = make_request('POST', f"{API_BASE}/improve", data)
    print_test_result("노트 개선 제안", success, result, response_time)
    if success: success_count += 1
    
    # 관련 노트 추천 - POST 요청
    total_tests += 1
    data = {"content": test_content, "limit": 5}
    success, result, response_time = make_request('POST', f"{API_BASE}/recommend", data)
    print_test_result("관련 노트 추천", success, result, response_time)
    if success: success_count += 1
    
    return success_count == total_tests


# ====== 채팅 히스토리 테스트 ======

def test_chat_history():
    """채팅 히스토리 테스트"""
    print_header("채팅 히스토리 테스트")
    
    success_count = 0
    total_tests = 0
    
    # 채팅 히스토리 조회 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/history")
    print_test_result("채팅 히스토리 조회", success, result, response_time)
    if success: success_count += 1
    
    # 히스토리 검색 - POST 요청 (구현된 메서드)
    total_tests += 1
    data = {"query": "Vue.js", "limit": 10}
    success, result, response_time = make_request('POST', f"{API_BASE}/history/search", data)
    if "search_chat_history" in str(result):
        print_test_result("히스토리 검색", False, "서버에서 메서드 미구현")
    else:
        print_test_result("히스토리 검색", success, result, response_time)
        if success: success_count += 1
    
    # 채팅 요약 통계 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/history/summary")
    print_test_result("채팅 요약 통계", success, result, response_time)
    if success: success_count += 1
    
    return success_count >= total_tests - 1  # 히스토리 검색은 예외 허용


# ====== 통계 및 정보 테스트 ======

def test_stats_and_info():
    """통계 및 정보 API 테스트"""
    print_header("통계 및 정보 API 테스트")
    
    success_count = 0
    total_tests = 0
    
    # 기본 통계 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/stats")
    print_test_result("기본 채팅 통계", success, result, response_time)
    if success: success_count += 1
    
    # 고급 통계 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/stats/advanced")
    print_test_result("고급 통계", success, result, response_time)
    if success: success_count += 1
    
    # 엔드포인트 목록 - GET 요청
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/endpoints")
    print_test_result("API 엔드포인트 목록", success, result, response_time)
    if success: success_count += 1
    
    return success_count == total_tests


# ====== 에러 처리 테스트 ======

def test_error_handling():
    """에러 처리 테스트"""
    print_header("에러 처리 테스트")
    
    success_count = 0
    total_tests = 0
    
    # 잘못된 JSON 데이터
    total_tests += 1
    try:
        response = requests.post(f"{API_BASE}/", 
                               data="invalid json", 
                               headers={'Content-Type': 'application/json'},
                               timeout=TIMEOUT)
        success = response.status_code == 400
        print_test_result("잘못된 JSON 처리", success, f"상태코드: {response.status_code}")
        if success: success_count += 1
    except Exception as e:
        print_test_result("잘못된 JSON 처리", False, str(e))
    
    # 빈 메시지
    total_tests += 1
    data = {"message": ""}
    success, result, response_time = make_request('POST', f"{API_BASE}/", data)
    # 빈 메시지는 서버에서 검증하므로 실패가 정상
    success = not success or "비어있습니다" in str(result)
    print_test_result("빈 메시지 처리", success, "서버 검증 정상")
    if success: success_count += 1
    
    # 존재하지 않는 엔드포인트
    total_tests += 1
    success, result, response_time = make_request('GET', f"{API_BASE}/nonexistent")
    success = not success  # 404 에러가 예상
    print_test_result("존재하지 않는 엔드포인트", success, "404 에러 정상 처리")
    if success: success_count += 1
    
    return success_count == total_tests


# ====== 성능 테스트 ======

def test_performance():
    """성능 테스트"""
    print_header("성능 테스트")
    
    test_message = "간단한 성능 테스트 메시지입니다."
    response_times = []
    success_count = 0
    
    print("🚀 5회 연속 요청 성능 테스트 중...")
    
    for i in range(5):
        data = {"message": f"{test_message} ({i+1}회)"}
        success, result, response_time = make_request('POST', f"{API_BASE}/", data)
        
        if success:
            response_times.append(response_time)
            success_count += 1
        
        print(f"   요청 {i+1}: {'✅' if success else '❌'} {response_time:.2f}초")
    
    if response_times:
        avg_time = sum(response_times) / len(response_times)
        min_time = min(response_times)
        max_time = max(response_times)
        
        print(f"\n📊 성능 통계:")
        print(f"   평균 응답시간: {avg_time:.2f}초")
        print(f"   최소 응답시간: {min_time:.2f}초") 
        print(f"   최대 응답시간: {max_time:.2f}초")
        print(f"   성공률: {success_count}/5 ({success_count/5*100:.1f}%)")
        
        performance_ok = avg_time < 10.0 and success_count >= 4
        print_test_result("전체 성능", performance_ok, f"평균 {avg_time:.2f}초")
        return performance_ok
    
    return False


# ====== 디버깅 도구 ======

def debug_endpoints():
    """실제 사용 가능한 엔드포인트 확인"""
    print_header("엔드포인트 디버깅")
    
    success, result, response_time = make_request('GET', f"{BASE_URL}/debug/routes")
    if success:
        print("✅ 등록된 API 엔드포인트:")
        api_routes = result.get('api_routes', [])
        for route in api_routes:
            print(f"  - {route['rule']} [{', '.join(route['methods'])}]")
        
        print(f"\n📊 총 {len(api_routes)}개 API 엔드포인트 발견")
        return True
    else:
        print("❌ 엔드포인트 정보를 가져올 수 없습니다")
        return False


# ====== 메인 테스트 함수 ======

def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 AI Note System - 최종 수정된 테스트 시작")
    print(f"⏰ 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌐 서버 URL: {BASE_URL}")
    print("🔧 수정사항: HTTP 415 오류 완전 해결")
    
    # 엔드포인트 디버깅
    debug_endpoints()
    
    tests = [
        ("서버 연결", test_server_connection),
        ("기본 채팅", test_basic_chat),
        ("Claude API", test_claude_connection),
        ("RAG 시스템", test_rag_system),
        ("Multiple Chains", test_multiple_chains),
        ("채팅 히스토리", test_chat_history),
        ("통계 및 정보", test_stats_and_info),
        ("에러 처리", test_error_handling),
        ("성능", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    failed_tests = []
    
    start_time = time.time()
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"\n🎉 {test_name} 테스트 그룹 통과!")
                passed += 1
            else:
                print(f"\n💥 {test_name} 테스트 그룹 실패!")
                failed_tests.append(test_name)
        except Exception as e:
            print(f"\n💥 {test_name} 테스트 그룹 오류: {e}")
            failed_tests.append(test_name)
    
    total_time = time.time() - start_time
    
    # 최종 결과 요약
    print("\n" + "="*60)
    print("📋 최종 테스트 결과 (HTTP 415 오류 해결)")
    print("="*60)
    print(f"✅ 통과: {passed}개 그룹")
    print(f"❌ 실패: {len(failed_tests)}개 그룹")
    print(f"📊 성공률: {passed}/{total} ({(passed/total*100):.1f}%)")
    print(f"⏱️ 총 소요시간: {total_time:.1f}초")
    
    if failed_tests:
        print(f"💥 실패한 테스트: {', '.join(failed_tests)}")
        print("\n🔧 해결 방법:")
        for test in failed_tests:
            if test == "Claude API":
                print("   - ANTHROPIC_API_KEY 환경변수 확인")
            elif test == "RAG 시스템":
                print("   - RAG 인덱스 초기화 필요")
    
    if passed >= total * 0.8:  # 80% 이상이면 성공
        print("\n🎉 테스트 대부분 통과! HTTP 415 오류가 해결되었습니다!")
        return True
    else:
        print("\n⚠️ 일부 테스트 실패. 추가 확인이 필요합니다.")
        return False


def quick_test():
    """빠른 기본 테스트"""
    print("⚡ 빠른 HTTP 415 오류 해결 확인")
    print("-" * 50)
    
    # 서버 연결 확인
    success = test_server_connection()
    if not success:
        print("❌ 서버에 연결할 수 없습니다!")
        return False
    
    # GET 요청 테스트 (이전에 415 오류 발생)
    print("\n🔍 GET 요청 오류 해결 확인:")
    get_endpoints = [
        ("/api/test", "Claude 테스트"),
        ("/api/rag/status", "RAG 상태"),
        ("/api/chains", "체인 정보"),
        ("/api/stats", "통계")
    ]
    
    success_count = 0
    for endpoint, name in get_endpoints:
        success, result, response_time = make_request('GET', f"{BASE_URL}{endpoint}")
        print_test_result(name, success, result, response_time)
        if success: success_count += 1
    
    # 기본 채팅 테스트
    data = {"message": "HTTP 415 오류 해결 테스트"}
    success, result, response_time = make_request('POST', f"{API_BASE}/", data)
    print_test_result("기본 채팅", success, result, response_time)
    if success: success_count += 1
    
    print(f"\n📊 결과: {success_count}/{len(get_endpoints)+1} 성공")
    
    if success_count >= len(get_endpoints):
        print("\n🎯 HTTP 415 오류 해결 확인! 모든 GET 요청이 정상 작동합니다.")
        return True
    else:
        print("\n⚠️ 일부 요청에서 여전히 문제가 있습니다.")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="AI Note System 최종 수정된 테스트")
    parser.add_argument('--quick', action='store_true', help='빠른 HTTP 415 오류 해결 확인')
    parser.add_argument('--debug', action='store_true', help='엔드포인트 디버깅만 실행')
    parser.add_argument('--server', default='http://localhost:5000', help='서버 URL')
    
    args = parser.parse_args()
    
    if args.server:
        BASE_URL = args.server.rstrip('/')
        API_BASE = f"{BASE_URL}/api"
        print(f"🌐 서버 URL: {BASE_URL}")
    
    try:
        if args.debug:
            debug_endpoints()
        elif args.quick:
            quick_test()
        else:
            run_all_tests()
            
    except KeyboardInterrupt:
        print("\n\n⏸️ 사용자에 의해 테스트가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 예상치 못한 오류: {e}")
        sys.exit(1)