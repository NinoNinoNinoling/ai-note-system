# backend/run.py
"""
완전히 수정된 서버 실행 파일

✅ 개선사항:
1. 포괄적인 에러 처리
2. 환경 체크 및 경고
3. 개발/프로덕션 모드 구분
4. 깔끔한 시작 메시지
5. 종료 처리 개선
"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_logging():
    """로깅 설정"""
    log_level = logging.DEBUG if os.getenv('FLASK_DEBUG', 'True').lower() == 'true' else logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # 외부 라이브러리 로그 레벨 조정
    logging.getLogger('werkzeug').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

def check_environment():
    """환경 변수 및 의존성 체크"""
    warnings = []
    errors = []
    
    # 필수 환경 변수 체크
    required_env_vars = ['SECRET_KEY']
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"환경 변수 {var}가 설정되지 않았습니다")
    
    # 선택적 환경 변수 체크
    optional_env_vars = {
        'ANTHROPIC_API_KEY': 'Claude AI 기능이 제한됩니다',
        'DATABASE_URL': '기본 SQLite 데이터베이스를 사용합니다'
    }
    
    for var, warning_msg in optional_env_vars.items():
        if not os.getenv(var):
            warnings.append(f"{var} 미설정: {warning_msg}")
    
    # 필수 디렉토리 체크
    required_dirs = ['data', 'models', 'app']
    for dir_name in required_dirs:
        if not os.path.exists(dir_name):
            warnings.append(f"디렉토리 {dir_name}이 없습니다")
    
    return warnings, errors

def print_startup_banner():
    """시작 배너 출력"""
    print("\n" + "="*50)
    print("🧠 AI Note System - 과제용 버전")
    print("="*50)
    print(f"📍 서버: http://localhost:5000")
    print(f"🔍 상태: http://localhost:5000/health")
    print(f"📝 노트: http://localhost:5000/api/notes")
    print(f"🤖 채팅: http://localhost:5000/api/chat")
    print("="*50)

def create_app_with_error_handling():
    """에러 처리가 포함된 앱 생성"""
    try:
        from app import create_app
        app = create_app()
        return app, None
    except ImportError as e:
        return None, f"앱 모듈 임포트 실패: {e}"
    except Exception as e:
        return None, f"앱 생성 실패: {e}"

def main():
    """메인 실행 함수"""
    # 로깅 설정
    setup_logging()
    logger = logging.getLogger(__name__)
    
    print_startup_banner()
    
    try:
        # 환경 체크
        warnings, errors = check_environment()
        
        # 에러가 있으면 종료
        if errors:
            print("\n❌ 심각한 오류:")
            for error in errors:
                print(f"   - {error}")
            print("\n.env 파일을 확인하고 다시 시도해주세요.")
            sys.exit(1)
        
        # 경고가 있으면 출력
        if warnings:
            print("\n⚠️ 경고사항:")
            for warning in warnings:
                print(f"   - {warning}")
        
        # Flask 앱 생성
        print("\n🚀 서버 시작!")
        app, error = create_app_with_error_handling()
        
        if error:
            print(f"\n❌ 앱 생성 실패: {error}")
            sys.exit(1)
        
        if not app:
            print("\n❌ 앱이 생성되지 않았습니다")
            sys.exit(1)
        
        # 개발 서버 설정
        debug_mode = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
        host = os.getenv('FLASK_HOST', '127.0.0.1')
        port = int(os.getenv('FLASK_PORT', 5000))
        
        # 서버 실행
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=debug_mode,
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n⏸️ 서버가 사용자에 의해 중단되었습니다.")
        print("👋 안전하게 종료됩니다...")
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ 포트 {port}가 이미 사용 중입니다.")
            print("다른 포트를 사용하거나 기존 프로세스를 종료해주세요.")
            print(f"💡 다른 포트로 실행: FLASK_PORT=5001 python run.py")
        else:
            print(f"\n❌ 네트워크 오류: {e}")
        sys.exit(1)
        
    except ImportError as e:
        print(f"\n❌ 모듈 임포트 실패: {e}")
        print("💡 의존성을 설치해주세요: pip install -r requirements.txt")
        sys.exit(1)
        
    except Exception as e:
        logger.exception("예상치 못한 오류 발생")
        print(f"\n❌ 예상치 못한 오류: {e}")
        print("💡 로그를 확인하고 문제를 해결해주세요.")
        sys.exit(1)
        
    finally:
        print(f"\n📝 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()