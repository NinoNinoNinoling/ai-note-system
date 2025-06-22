# backend/app.py - 리팩토링된 메인 애플리케이션
from flask import Flask, jsonify
from datetime import datetime
from sqlalchemy import text
from config.settings import Config
from config.database import init_db, db
from app.routes.notes import notes_bp
from app.routes.chat import chat_bp

def create_app():
    """Flask 애플리케이션 팩토리"""
    
    # Flask 앱 생성
    app = Flask(__name__)
    
    # 설정 로드
    app.config.from_object(Config)
    
    # 설정 검증
    Config.validate()
    
    # 데이터베이스 초기화
    init_db(app)
    
    # Blueprint 등록
    app.register_blueprint(notes_bp, url_prefix='/api/notes')
    app.register_blueprint(chat_bp, url_prefix='/api/chat')
    
    # 기본 라우트들
    register_basic_routes(app)
    
    return app

def register_basic_routes(app):
    """기본 라우트 등록"""
    
    @app.route('/')
    def index():
        """메인 페이지 - 시스템 상태"""
        from models.note import Note
        from chains.rag_chain import rag_chain
        
        try:
            note_count = Note.query.count()
            rag_stats = rag_chain.get_stats()
            
            return jsonify({
                "message": "🧠 AI Note System",
                "version": "1.0.0",
                "status": "running",
                "timestamp": datetime.now().isoformat(),
                "features": {
                    "notes": {
                        "total_notes": note_count,
                        "crud_operations": True,
                        "tag_system": True,
                        "search": True
                    },
                    "ai": {
                        "claude_api": bool(Config.ANTHROPIC_API_KEY),
                        "rag_system": rag_stats["available"],
                        "chat_history": True
                    },
                    "rag": rag_stats
                },
                "api_endpoints": {
                    "notes": "/api/notes",
                    "chat": "/api/chat", 
                    "rag_chat": "/api/chat/rag",
                    "search": "/api/notes/search"
                }
            })
            
        except Exception as e:
            return jsonify({
                "message": "🧠 AI Note System",
                "status": "error",
                "timestamp": datetime.now().isoformat(),
                "error": str(e)
            }), 500
    
    @app.route('/health')
    def health_check():
        """헬스 체크"""
        try:
            # DB 연결 확인 (SQLAlchemy 2.0+ 호환)
            db.session.execute(text('SELECT 1'))
            
            return jsonify({
                "status": "healthy",
                "database": "connected",
                "timestamp": datetime.now().isoformat(),
                "version": "1.0.0"
            })
            
        except Exception as e:
            return jsonify({
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 503
    
    @app.route('/api/info')
    def api_info():
        """API 정보"""
        return jsonify({
            "api_version": "v1",
            "server_time": datetime.now().isoformat(),
            "endpoints": {
                "notes": {
                    "GET /api/notes": "노트 목록 조회",
                    "POST /api/notes": "노트 생성",
                    "GET /api/notes/<id>": "노트 상세 조회",
                    "PUT /api/notes/<id>": "노트 수정",
                    "DELETE /api/notes/<id>": "노트 삭제",
                    "POST /api/notes/search": "노트 검색",
                    "GET /api/notes/tags": "태그 목록",
                    "GET /api/notes/stats": "노트 통계"
                },
                "chat": {
                    "POST /api/chat": "AI 채팅",
                    "POST /api/chat/rag": "RAG 기반 AI 채팅",
                    "GET /api/chat/test": "Claude API 테스트",
                    "GET /api/chat/history": "채팅 기록",
                    "DELETE /api/chat/history/<id>": "채팅 삭제",
                    "POST /api/chat/rag/rebuild": "RAG 인덱스 재구축"
                },
                "system": {
                    "GET /": "시스템 상태",
                    "GET /health": "헬스 체크",
                    "GET /api/info": "API 정보"
                }
            },
            "authentication": "None (개발 버전)",
            "rate_limiting": "None (개발 버전)",
            "documentation": "Built-in API documentation"
        })
    
    @app.route('/test-db')
    def test_db():
        """데이터베이스 테스트 (개발용)"""
        try:
            from models.note import Note
            
            # DB 테이블 생성 확인
            db.create_all()
            
            # 테스트 노트 생성
            test_note = Note(
                title="시스템 테스트 노트",
                content=f"리팩토링 완료 테스트 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            )
            test_note.set_tags(["시스템", "테스트", "리팩토링"])
            
            db.session.add(test_note)
            db.session.commit()
            
            return jsonify({
                "status": "✅ DB 테스트 성공!",
                "test_note": test_note.to_dict(),
                "total_notes": Note.query.count(),
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "status": "❌ DB 테스트 실패",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }), 500
    
    @app.errorhandler(404)
    def not_found(error):
        """404 오류 처리"""
        return jsonify({
            "error": "엔드포인트를 찾을 수 없습니다",
            "message": "올바른 API 경로를 확인해주세요",
            "api_info": "/api/info",
            "timestamp": datetime.now().isoformat()
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """500 오류 처리"""
        db.session.rollback()
        return jsonify({
            "error": "서버 내부 오류",
            "message": "문제가 지속되면 관리자에게 문의하세요",
            "timestamp": datetime.now().isoformat()
        }), 500

# 개발 서버 실행
if __name__ == '__main__':
    app = create_app()
    
    print("=" * 60)
    print("🧠 AI Note System - 리팩토링 완료!")
    print("=" * 60)
    print("📍 서버: http://localhost:5000")
    print("📖 API 정보: http://localhost:5000/api/info")
    print("🔍 헬스 체크: http://localhost:5000/health")
    print("🧪 DB 테스트: http://localhost:5000/test-db")
    print("")
    print("📝 노트 API:")
    print("   GET    /api/notes              - 노트 목록")
    print("   POST   /api/notes              - 노트 생성")
    print("   GET    /api/notes/<id>         - 노트 조회")
    print("   PUT    /api/notes/<id>         - 노트 수정")
    print("   DELETE /api/notes/<id>         - 노트 삭제")
    print("   POST   /api/notes/search       - 노트 검색")
    print("")
    print("💬 AI 채팅 API:")
    print("   POST   /api/chat               - 기본 AI 채팅")
    print("   POST   /api/chat/rag           - RAG 기반 채팅")
    print("   GET    /api/chat/test          - Claude API 테스트")
    print("   POST   /api/chat/rag/rebuild   - RAG 인덱스 재구축")
    print("=" * 60)
    
    # 설정 확인
    if Config.ANTHROPIC_API_KEY:
        print("✅ Claude API 키 설정됨")
    else:
        print("⚠️ Claude API 키가 설정되지 않음 (Mock 응답 사용)")
    
    # DB 경로 출력
    db_path = Config.get_db_path()
    if db_path:
        print(f"📁 DB 파일: {db_path}")
    
    print("🕐 시작 시간:", datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    print("=" * 60)
    
    app.run(debug=True, host='localhost', port=5000)