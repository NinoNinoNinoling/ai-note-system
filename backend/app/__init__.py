# app/__init__.py - Flask 앱 팩토리
"""
AI Note System - Flask 애플리케이션 팩토리

모듈화된 Flask 앱 구조
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime


def create_app():
    """Flask 애플리케이션 팩토리 함수"""
    
    # Flask 앱 생성
    app = Flask(__name__)
    
    # 설정 로드
    from config.settings import Config
    app.config.from_object(Config)
    
    # CORS 설정 (개발용 - 모든 도메인 허용)
    CORS(app, resources={
        r"/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # 추가적인 CORS 헤더 설정
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response
    
    # 데이터베이스 초기화
    from config.database import init_db
    init_db(app)
    
    # Blueprint 등록
    register_blueprints(app)
    
    # 기본 라우트 등록
    register_basic_routes(app)
    
    return app


def register_blueprints(app):
    """Blueprint들을 앱에 등록"""
    
    try:
        # 시스템 라우트
        from app.routes.system import system_bp
        app.register_blueprint(system_bp)
        
        # 노트 라우트  
        from app.routes.notes import notes_bp
        app.register_blueprint(notes_bp, url_prefix='/api')
        
        # 채팅 라우트
        from app.routes.chat import chat_bp
        app.register_blueprint(chat_bp, url_prefix='/api')
        
        print("✅ 모든 Blueprint 등록 완료")
        
    except ImportError as e:
        print(f"⚠️ Blueprint 임포트 실패: {e}")
        print("💡 기본 라우트만 사용합니다")


def register_basic_routes(app):
    """기본 라우트들 등록"""
    
    @app.route('/')
    def home():
        """홈 페이지"""
        return jsonify({
            "message": "🧠 AI Note System",
            "version": "1.0.0",
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "health": "/health",
                "notes": "/api/notes", 
                "chat": "/api/chat"
            }
        })
    
    @app.route('/health')
    def health():
        """헬스 체크"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cors": "enabled"
        })
    
    @app.route('/api/notes')
    def get_notes_basic():
        """기본 노트 API (Blueprint 없을 때 대체)"""
        sample_notes = [
            {
                "id": 1,
                "title": "🎉 백엔드 구조 개편 완료!",
                "content": "# 성공!\n\nFlask 앱 팩토리 패턴 적용 완료",
                "tags": ["success", "flask", "restructure"],
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
        ]
        
        return jsonify({
            "notes": sample_notes,
            "total": len(sample_notes),
            "message": "기본 노트 API 작동 중"
        })
    
    @app.errorhandler(404)
    def not_found(error):
        """404 에러 처리"""
        return jsonify({
            "error": "Not Found",
            "message": "요청한 리소스를 찾을 수 없습니다",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 에러 처리"""
        return jsonify({
            "error": "Internal Server Error", 
            "message": "서버 내부 오류가 발생했습니다",
            "timestamp": datetime.now().isoformat()
        }), 500