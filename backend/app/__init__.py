# backend/app/__init__.py
"""
AI Note System - Flask 애플리케이션 팩토리

SPA(dist) 자동 서빙 + API 네임스페이스 분리 + 슬래시 유연 매칭
"""

import os
from datetime import datetime
from flask import Flask, jsonify, send_from_directory, abort
from flask_cors import CORS

from config.database import init_db, db
from models.note import Note  # 통계용

def create_app():
    """Flask 애플리케이션 팩토리"""
    # ─────────────────────────────────────────────────
    # 1) Vue 배포용 dist 경로 자동 계산
    BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    vue_dist = os.path.join(BASE_DIR, 'frontend', 'ai-note-frontend', 'dist')
    if not os.path.isdir(vue_dist):
        raise RuntimeError(f"Vue dist 폴더를 찾을 수 없습니다: {vue_dist}")

    # ─────────────────────────────────────────────────
    # 2) Flask 앱 생성: dist를 static_folder로 지정
    app = Flask(
        __name__,
        static_folder=vue_dist,
        static_url_path=''   # /assets, /favicon.ico 등을 dist 아래에서 바로 서빙
    )

    # 3) 슬래시 매칭 유연화 (strict_slashes 해제)
    app.url_map.strict_slashes = False

    # ─────────────────────────────────────────────────
    # 4) 설정 로드
    from config.settings import Config
    app.config.from_object(Config)

    # ─────────────────────────────────────────────────
    # 5) CORS 설정
    origins = os.getenv('CORS_ORIGINS', '').split(',')
    if not origins or origins == ['']:
        origins = ['http://localhost:5173', 'http://127.0.0.1:5173']
    CORS(app,
         origins=origins,
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
         allow_headers=['Content-Type', 'Authorization'],
         supports_credentials=True)

    # ─────────────────────────────────────────────────
    # 6) DB 초기화
    init_db(app)

    # ─────────────────────────────────────────────────
    # 7) Blueprint 등록
    register_blueprints(app)

    # ─────────────────────────────────────────────────
    # 8) 기본 API 라우트 등록
    register_basic_routes(app)

    # ─────────────────────────────────────────────────
    # 9) SPA catch-all: /api/* 는 API, 나머지 모두 index.html
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # API로 넘어갈 요청
        if path.startswith('api/'):
            abort(404)

        # 정적 파일이 있으면 서빙
        full = os.path.join(app.static_folder, path)
        if path and os.path.exists(full):
            return send_from_directory(app.static_folder, path)

        # 나머지는 SPA 엔트리포인트
        return send_from_directory(app.static_folder, 'index.html')

    # ─────────────────────────────────────────────────
    # 10) 디버그: dist 경로 & 엔드포인트 목록
    print(f"▶ Serving Vue dist from: {app.static_folder}")
    print(f"▶ dist contents: {os.listdir(app.static_folder)}")
    print_registered_endpoints(app)

    return app


def register_blueprints(app):
    """Blueprint들을 앱에 등록"""
    from app.routes.system import system_bp
    from app.routes.notes import notes_bp
    from app.routes.chat import chat_bp

    # system APIs under /api/system
    app.register_blueprint(system_bp, url_prefix='/api/system')
    # notes, chat under /api
    app.register_blueprint(notes_bp, url_prefix='/api')
    app.register_blueprint(chat_bp,  url_prefix='/api')

    print("✅ 모든 Blueprint 등록 완료")


def register_basic_routes(app):
    """기본 API(route) 정의"""

    @app.route('/api/info')
    def info():
        """서비스 정보 & 주요 엔드포인트 안내"""
        try:
            total_notes = db.session.query(Note).count()
        except Exception:
            total_notes = 'N/A'

        return jsonify({
            "service": "🧠 AI Note System",
            "version": app.config.get('VERSION', '1.0.0'),
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "database": "connected",
                "total_notes": total_notes
            },
            "endpoints": {
                "notes":   "/api/notes",
                "chat":    "/api/",
                "health":  "/health",
                "system":  "/api/system/"
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

    @app.route('/debug/routes')
    def debug_routes():
        """등록된 라우트 정보 반환"""
        routes = []
        for rule in app.url_map.iter_rules():
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            routes.append({
                "rule":     rule.rule,
                "methods":  methods,
                "endpoint": rule.endpoint
            })
        return jsonify({
            "total_routes": len(routes),
            "routes":       sorted(routes, key=lambda x: x['rule']),
            "api_routes":   [r for r in routes if r['rule'].startswith('/api/')],
            "timestamp":    datetime.now().isoformat()
        })

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error":     "Not Found",
            "message":   "요청한 리소스를 찾을 수 없습니다",
            "timestamp": datetime.now().isoformat()
        }), 404

    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error":     "Internal Server Error",
            "message":   "서버 내부 오류가 발생했습니다",
            "timestamp": datetime.now().isoformat()
        }), 500


def print_registered_endpoints(app):
    """등록된 모든 엔드포인트 출력 (디버깅용)"""
    print("\n" + "="*60)
    print("🔍 등록된 Flask 엔드포인트 목록")
    print("="*60)

    grouped = {}
    for rule in app.url_map.iter_rules():
        bp = rule.endpoint.split('.')[0] if '.' in rule.endpoint else 'main'
        grouped.setdefault(bp, []).append(rule)

    for bp, rules in grouped.items():
        print(f"\n📂 {bp.upper()} Blueprint:")
        print("-"*40)
        for rule in sorted(rules, key=lambda r: r.rule):
            methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
            print(f"  {rule.rule:<30} [{', '.join(methods)}] -> {rule.endpoint}")

    total = sum(len(rules) for rules in grouped.values())
    print(f"\n✅ 총 {total}개 엔드포인트 등록됨")
    print("="*60 + "\n")

    print("🚀 주요 API 엔드포인트:")
    api_rules = [r for r in app.url_map.iter_rules() if r.rule.startswith('/api/')]
    for rule in sorted(api_rules, key=lambda r: r.rule):
        methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
        print(f"  {rule.rule} [{', '.join(methods)}]")
    print(f"\n✅ {len(api_rules)}개 API 엔드포인트 정상 등록\n")