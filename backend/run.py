# backend/run.py
"""
디버깅 강화된 서버 실행 파일

모든 요청과 응답을 상세하게 로깅
"""

import os
import sys
import logging
from datetime import datetime

# 프로젝트 루트 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def setup_enhanced_logging():
    """강화된 로깅 설정"""
    
    # 모든 로거를 DEBUG 레벨로 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)
    
    # 콘솔 핸들러 설정
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    
    # 상세한 포맷터 설정
    detailed_formatter = logging.Formatter(
        '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d - %(message)s'
    )
    console_handler.setFormatter(detailed_formatter)
    
    # 루트 로거에 핸들러 추가
    root_logger.addHandler(console_handler)
    
    # 주요 로거들 DEBUG 레벨로 설정
    important_loggers = [
        'app.routes.notes',
        'app.controllers.note_controller', 
        'app.services.note_service',
        'app.repositories.note_repository',
        'sqlalchemy.engine',
        'flask',
        'werkzeug'
    ]
    
    for logger_name in important_loggers:
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = True
    
    # SQLAlchemy 쿼리 로깅 활성화
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)
    logging.getLogger('sqlalchemy.pool').setLevel(logging.INFO)
    
    print("✅ 강화된 디버깅 로깅 설정 완료")

def print_startup_banner():
    """시작 배너 출력"""
    print("\n" + "="*60)
    print("🧠 AI Note System - 디버깅 모드")
    print("="*60)
    print(f"📍 서버: http://localhost:5000")
    print(f"🔍 상태: http://localhost:5000/health")
    print(f"📝 노트: http://localhost:5000/api/notes")
    print(f"🧪 테스트: http://localhost:5000/api/notes/test")
    print(f"🤖 채팅: http://localhost:5000/api/")
    print("="*60)
    print("🔍 모든 API 요청이 상세하게 로깅됩니다")
    print("="*60)

def create_app_with_debug():
    """디버깅이 강화된 앱 생성"""
    try:
        from app import create_app
        
        print("🚀 Flask 앱 생성 중...")
        app = create_app()
        
        # Flask 앱 로깅 설정
        app.logger.setLevel(logging.DEBUG)
        
        # 요청 로깅 미들웨어 추가
        @app.before_request
        def log_request_info():
            from flask import request
            print(f"\n{'🔥'*50}")
            print(f"📥 들어온 요청: {request.method} {request.path}")
            print(f"📥 Full URL: {request.url}")
            print(f"📥 Remote IP: {request.remote_addr}")
            print(f"📥 User Agent: {request.headers.get('User-Agent', 'Unknown')}")
            if request.args:
                print(f"📥 Query Params: {dict(request.args)}")
            
            # 🔧 안전한 JSON 파싱으로 수정
            if request.is_json:
                try:
                    json_data = request.get_json(silent=True)
                    if json_data is not None:
                        print(f"📥 JSON Data: {json_data}")
                    else:
                        print(f"📥 JSON Data: (빈 JSON 또는 파싱 실패)")
                except Exception as e:
                    print(f"📥 JSON Data: 파싱 에러 - {e}")
            
            print(f"{'🔥'*50}")
        
        @app.after_request  
        def log_response_info(response):
            print(f"\n{'🚀'*50}")
            print(f"📤 응답: {response.status}")
            print(f"📤 Content-Type: {response.content_type}")
            print(f"📤 Content-Length: {response.content_length}")
            
            # JSON 응답인 경우 내용 일부 출력
            if response.content_type and 'application/json' in response.content_type:
                try:
                    response_data = response.get_json()
                    if response_data:
                        print(f"📤 Response Keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Not a dict'}")
                        if isinstance(response_data, dict) and 'notes' in response_data:
                            notes = response_data['notes']
                            print(f"📤 Notes Count: {len(notes) if notes else 0}")
                except:
                    print(f"📤 Response Body: {response.get_data()[:200]}...")
            
            print(f"{'🚀'*50}\n")
            return response
        
        print("✅ Flask 앱 생성 완료")
        return app, None
        
    except Exception as e:
        print(f"❌ 앱 생성 실패: {e}")
        import traceback
        traceback.print_exc()
        return None, f"앱 생성 실패: {e}"

def main():
    """메인 실행 함수"""
    
    print_startup_banner()
    
    # 강화된 로깅 설정
    setup_enhanced_logging()
    
    try:
        # Flask 앱 생성
        print("\n🚀 서버 시작!")
        app, error = create_app_with_debug()
        
        if error:
            print(f"\n❌ 앱 생성 실패: {error}")
            sys.exit(1)
        
        if not app:
            print("\n❌ 앱이 생성되지 않았습니다")
            sys.exit(1)
        
        # 개발 서버 설정
        debug_mode = True  # 강제로 디버그 모드
        host = '127.0.0.1'
        port = 5000
        
        print(f"\n🎯 서버 설정:")
        print(f"   - Host: {host}")
        print(f"   - Port: {port}")
        print(f"   - Debug: {debug_mode}")
        print(f"   - Threaded: True")
        
        print(f"\n🚀 서버 실행 중...")
        print(f"브라우저에서 http://localhost:5000/api/notes 접속해보세요!")
        
        # 서버 실행
        app.run(
            host=host,
            port=port,
            debug=debug_mode,
            use_reloader=False,  # 리로더 비활성화 (로그 중복 방지)
            threaded=True
        )
        
    except KeyboardInterrupt:
        print("\n\n⏸️ 서버가 사용자에 의해 중단되었습니다.")
        print("👋 안전하게 종료됩니다...")
        
    except OSError as e:
        if "Address already in use" in str(e):
            print(f"\n❌ 포트 5000이 이미 사용 중입니다.")
            print("기존 서버를 종료하고 다시 시도해주세요.")
        else:
            print(f"\n❌ 네트워크 오류: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n❌ 예상치 못한 오류: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        print(f"\n📝 종료 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()