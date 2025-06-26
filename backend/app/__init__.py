# backend/app/__init__.py
"""
AI Note System - Flask 애플리케이션 팩토리

모듈화된 Flask 앱 구조 (라우트 중복 문제 해결)
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
    
    # ✅ CORS 설정 (하나만 사용!)
    CORS(app, 
         origins=['http://localhost:5173', 'http://127.0.0.1:5173'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True
    )
    
    # 데이터베이스 초기화
    from config.database import init_db
    init_db(app)
    
    # Blueprint 등록
    register_blueprints(app)
    
    # 기본 라우트 등록
    register_basic_routes(app)
    
    # 🔍 등록된 엔드포인트 디버깅 출력
    print_registered_endpoints(app)
    
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
                "chat": "/api/"
            }
        })
    
    @app.route('/health')
    def health():
        """헬스 체크"""
        return jsonify({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "cors": "enabled - flask-cors only"
        })
    
    @app.route('/debug/routes')
    def debug_routes():
        """등록된 라우트 정보 (웹에서 확인용)"""
        routes = []
        for rule in app.url_map.iter_rules():
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            routes.append({
                'rule': rule.rule,
                'methods': methods,
                'endpoint': rule.endpoint
            })
        
        return jsonify({
            "total_routes": len(routes),
            "routes": sorted(routes, key=lambda x: x['rule']),
            "api_routes": [r for r in routes if r['rule'].startswith('/api/')],
            "timestamp": datetime.now().isoformat()
        })
    
    # ❌ 중복 라우트 제거: /api/notes는 NOTES Blueprint에서 처리
    # @app.route('/api/notes')
    # def get_notes_basic():
    #     """기본 노트 API (Blueprint 없을 때 대체) - 제거됨"""
    #     pass
    
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


def print_registered_endpoints(app):
    """등록된 모든 엔드포인트 출력 (디버깅용)"""
    print("\n" + "="*60)
    print("🔍 등록된 Flask 엔드포인트 목록")
    print("="*60)
    
    # 라우트별로 정리
    routes_by_blueprint = {}
    
    for rule in app.url_map.iter_rules():
        # Blueprint 정보 추출
        endpoint = rule.endpoint
        blueprint_name = endpoint.split('.')[0] if '.' in endpoint else 'main'
        
        if blueprint_name not in routes_by_blueprint:
            routes_by_blueprint[blueprint_name] = []
            
        # 메소드 정리
        methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
        
        routes_by_blueprint[blueprint_name].append({
            'rule': rule.rule,
            'methods': methods,
            'endpoint': endpoint
        })
    
    # Blueprint별로 출력
    for blueprint, routes in routes_by_blueprint.items():
        print(f"\n📂 {blueprint.upper()} Blueprint:")
        print("-" * 40)
        
        for route in sorted(routes, key=lambda x: x['rule']):
            methods_str = ', '.join(route['methods'])
            print(f"  {route['rule']:<30} [{methods_str}] -> {route['endpoint']}")
    
    print(f"\n✅ 총 {sum(len(routes) for routes in routes_by_blueprint.values())}개 엔드포인트 등록됨")
    print("="*60 + "\n")
    
    # API 엔드포인트만 별도 출력
    print("🚀 주요 API 엔드포인트:")
    print("-" * 30)
    api_endpoints = []
    for rule in app.url_map.iter_rules():
        if rule.rule.startswith('/api/'):
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            api_endpoints.append(f"  {rule.rule} [{', '.join(methods)}]")
    
    for endpoint in sorted(api_endpoints):
        print(endpoint)
    
    if not api_endpoints:
        print("  ⚠️ /api/ 엔드포인트가 등록되지 않았습니다!")
        print("  💡 Blueprint 등록 확인 필요")
    else:
        print(f"\n✅ {len(api_endpoints)}개 API 엔드포인트 정상 등록")
    
    print("\n")