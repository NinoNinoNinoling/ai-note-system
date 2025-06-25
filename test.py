# backend/tests/test_chains.py
"""
Multiple Chains 단위 테스트

프로덕션 코드와 완전히 분리된 테스트 파일
개발 중 체인 기능을 독립적으로 테스트할 때 사용
"""

import sys
import os
from datetime import datetime

# 상위 디렉토리를 Python 경로에 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))


def test_chains_basic():
    """기본 체인 기능 테스트"""
    print("🔥 Multiple Chains 기본 테스트")
    print("=" * 50)
    
    try:
        from chains.specialized_chains import (
            chain_manager,
            summarize_note,
            analyze_note,
            recommend_notes,
            improve_note,
            CHAINS_AVAILABLE
        )
        
        print(f"✅ Import 성공: CHAINS_AVAILABLE = {CHAINS_AVAILABLE}")
        
    except ImportError as e:
        print(f"❌ Import 실패: {e}")
        return False
    
    # 체인 정보 확인
    chains_info = chain_manager.get_chains_info()
    print(f"📊 체인 정보: {chains_info}")
    
    return True


def test_summarization_chain():
    """요약 체인 테스트"""
    print("\n📝 요약 체인 테스트")
    print("-" * 30)
    
    test_note = """
# Vue.js 학습 노트

## 기본 개념
- 반응형 데이터
- 컴포넌트 시스템
- 디렉티브

## Composition API
- ref()
- reactive()
- computed()
"""
    
    try:
        from chains.specialized_chains import summarize_note
        
        result = summarize_note(test_note, "Vue.js 기초 학습")
        
        if result.get('success'):
            print("✅ 요약 성공")
            print(f"📄 요약 내용: {result['summary'][:100]}...")
            return True
        else:
            print(f"❌ 요약 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 요약 테스트 오류: {e}")
        return False


def test_analysis_chain():
    """분석 체인 테스트"""
    print("\n🔍 분석 체인 테스트")
    print("-" * 30)
    
    test_note = """
# Python Flask 웹 개발

## 기본 설정
Flask는 마이크로 웹 프레임워크입니다.

## Blueprint 활용
- 모듈화된 앱 구조
- 라우트 분리
"""
    
    try:
        from chains.specialized_chains import analyze_note
        
        result = analyze_note(test_note, "Flask 학습")
        
        if result.get('success'):
            print("✅ 분석 성공")
            print(f"📊 분석 내용: {result['analysis'][:100]}...")
            return True
        else:
            print(f"❌ 분석 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 분석 테스트 오류: {e}")
        return False


def test_recommendation_chain():
    """추천 체인 테스트"""
    print("\n🎯 추천 체인 테스트")
    print("-" * 30)
    
    current_note = "LangChain으로 AI 에이전트 만들기"
    
    dummy_notes = [
        {"id": 1, "title": "Python 기초", "content": "Python 변수와 함수"},
        {"id": 2, "title": "Flask 웹 개발", "content": "Flask 라우팅과 템플릿"}
    ]
    
    try:
        from chains.specialized_chains import recommend_notes
        
        result = recommend_notes(current_note, dummy_notes)
        
        if result.get('success'):
            print("✅ 추천 성공")
            print(f"💡 추천 내용: {result['recommendations'][:100]}...")
            return True
        else:
            print(f"❌ 추천 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 추천 테스트 오류: {e}")
        return False


def test_improvement_chain():
    """개선 체인 테스트"""
    print("\n⚡ 개선 체인 테스트")
    print("-" * 30)
    
    test_note = """
# 리액트 공부
컴포넌트 만들었음.
useState 썼음.
잘 모르겠음.
"""
    
    try:
        from chains.specialized_chains import improve_note
        
        result = improve_note(test_note, "React 학습")
        
        if result.get('success'):
            print("✅ 개선 성공")
            print(f"🔧 개선 내용: {result['improvements'][:100]}...")
            return True
        else:
            print(f"❌ 개선 실패: {result.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ 개선 테스트 오류: {e}")
        return False


def test_chain_manager():
    """체인 매니저 테스트"""
    print("\n🔗 체인 매니저 테스트")
    print("-" * 30)
    
    try:
        from chains.specialized_chains import chain_manager
        
        # 사용 가능한 체인 확인
        available_chains = chain_manager.get_available_chains()
        print(f"✅ 사용 가능한 체인: {available_chains}")
        
        # 각 체인별 상태 확인
        for chain_type in ['summarization', 'analysis', 'recommendation', 'improvement']:
            is_available = chain_manager.is_available(chain_type)
            status = "✅" if is_available else "❌"
            print(f"  {status} {chain_type}: {is_available}")
        
        # 전체 정보 확인
        chains_info = chain_manager.get_chains_info()
        print(f"📊 전체 체인 정보: {chains_info}")
        
        return len(available_chains) > 0
        
    except Exception as e:
        print(f"❌ 체인 매니저 테스트 오류: {e}")
        return False


def test_error_handling():
    """에러 처리 테스트"""
    print("\n🛡️ 에러 처리 테스트")
    print("-" * 30)
    
    try:
        from chains.specialized_chains import summarize_note
        
        # 빈 내용 테스트
        result = summarize_note("", "")
        print(f"빈 내용 처리: {result}")
        
        # 매우 긴 내용 테스트
        long_content = "테스트 " * 1000
        result = summarize_note(long_content, "긴 내용 테스트")
        print(f"긴 내용 처리: {'성공' if result.get('success') else '실패'}")
        
        return True
        
    except Exception as e:
        print(f"❌ 에러 처리 테스트 실패: {e}")
        return False


def test_performance():
    """성능 테스트"""
    print("\n⚡ 성능 테스트")
    print("-" * 30)
    
    try:
        from chains.specialized_chains import summarize_note
        import time
        
        test_content = "# 테스트 노트\n\n간단한 내용입니다."
        
        # 10회 실행 시간 측정
        start_time = time.time()
        
        for i in range(3):  # 부하를 줄이기 위해 3회만
            result = summarize_note(test_content, f"테스트 {i+1}")
            if not result.get('success'):
                print(f"❌ {i+1}번째 테스트 실패")
                return False
        
        end_time = time.time()
        avg_time = (end_time - start_time) / 3
        
        print(f"✅ 평균 응답 시간: {avg_time:.2f}초")
        
        return avg_time < 30  # 30초 이내면 통과
        
    except Exception as e:
        print(f"❌ 성능 테스트 실패: {e}")
        return False


def run_all_tests():
    """모든 테스트 실행"""
    print("🚀 Multiple Chains 전체 테스트 시작")
    print("=" * 60)
    
    tests = [
        ("기본 기능", test_chains_basic),
        ("체인 매니저", test_chain_manager),
        ("요약 체인", test_summarization_chain),
        ("분석 체인", test_analysis_chain),
        ("추천 체인", test_recommendation_chain),
        ("개선 체인", test_improvement_chain),
        ("에러 처리", test_error_handling),
        ("성능", test_performance),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                print(f"✅ {test_name} 테스트 통과")
                passed += 1
            else:
                print(f"❌ {test_name} 테스트 실패")
        except Exception as e:
            print(f"❌ {test_name} 테스트 오류: {e}")
    
    # 결과 요약
    print("\n" + "=" * 60)
    print("📋 테스트 결과 요약")
    print("=" * 60)
    print(f"✅ 통과: {passed}개")
    print(f"❌ 실패: {total - passed}개")
    print(f"📊 성공률: {passed}/{total} ({(passed/total*100):.1f}%)")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과! Multiple Chains가 정상 작동합니다!")
    elif passed >= total * 0.8:
        print("\n✅ 대부분 테스트 통과. 시스템이 잘 작동하고 있습니다.")
    else:
        print("\n⚠️ 일부 테스트 실패. 확인이 필요합니다.")
    
    return passed == total


def quick_test():
    """빠른 테스트 (기본 기능만)"""
    print("⚡ Multiple Chains 빠른 테스트")
    print("-" * 40)
    
    try:
        # 임포트 테스트
        from chains.specialized_chains import CHAINS_AVAILABLE, chain_manager
        print(f"✅ 임포트 성공: CHAINS_AVAILABLE = {CHAINS_AVAILABLE}")
        
        # 체인 상태 확인
        available = chain_manager.get_available_chains()
        print(f"✅ 사용 가능한 체인: {available}")
        
        # 간단한 기능 테스트
        if available:
            from chains.specialized_chains import summarize_note
            result = summarize_note("테스트 노트", "빠른 테스트")
            
            if result.get('success'):
                print("✅ 기본 기능 작동 확인")
            else:
                print(f"⚠️ 기능 테스트 실패: {result.get('error')}")
        
        print("\n🎯 빠른 테스트 완료!")
        return True
        
    except Exception as e:
        print(f"❌ 빠른 테스트 실패: {e}")
        return False


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Multiple Chains 테스트")
    parser.add_argument('--quick', action='store_true', help='빠른 테스트만 실행')
    parser.add_argument('--unit', choices=['basic', 'manager', 'summarize', 'analyze', 'recommend', 'improve', 'error', 'performance'], help='특정 단위 테스트만 실행')
    
    args = parser.parse_args()
    
    if args.quick:
        quick_test()
    elif args.unit:
        test_map = {
            'basic': test_chains_basic,
            'manager': test_chain_manager,
            'summarize': test_summarization_chain,
            'analyze': test_analysis_chain,
            'recommend': test_recommendation_chain,
            'improve': test_improvement_chain,
            'error': test_error_handling,
            'performance': test_performance
        }
        
        test_func = test_map.get(args.unit)
        if test_func:
            print(f"🎯 {args.unit} 단위 테스트 실행")
            success = test_func()
            print(f"\n결과: {'✅ 성공' if success else '❌ 실패'}")
        else:
            print(f"❌ 알 수 없는 테스트: {args.unit}")
    else:
        run_all_tests()