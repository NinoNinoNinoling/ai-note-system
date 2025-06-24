# backend/run.py - 앱 구동 전용
"""
AI Note System - 서버 실행

python run.py 로 실행하세요
"""

from app import create_app
from config.settings import Config


def print_startup_info(app):
    """간단한 시작 정보 출력"""
    print("=" * 50)
    print("🧠 AI Note System - 과제용 버전")
    print("=" * 50)
    print(f"📍 서버: http://localhost:5000")
    print(f"🔍 상태: http://localhost:5000/health")  
    print(f"📝 노트: http://localhost:5000/api/notes")
    print(f"🤖 채팅: http://localhost:5000/api/chat")
    print("=" * 50)
    print("🚀 서버 시작!")


if __name__ == '__main__':
    # 앱 생성
    app = create_app()
    
    # 시작 정보 출력
    print_startup_info(app)
    
    # 개발 서버 실행
    app.run(
        debug=Config.DEBUG,
        host='localhost',
        port=5000
    )