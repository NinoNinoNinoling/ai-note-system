# backend/app/routes/system.py - 시스템 라우트
"""
시스템 관련 라우트 및 디버깅 기능

헬스체크, 상태 확인, 라우트 디버깅 등
"""

from flask import Blueprint, jsonify, current_app
from datetime import datetime
from sqlalchemy import text
from config.database import db

# Blueprint 생성
system_bp = Blueprint('system', __name__)


@system_bp.route('/')
def index():
    """메인 페이지 - 시스템 상태"""
    try:
        from models.note import Note
        note_count = Note.query.count()
        
        return jsonify({
            "service": "🧠 AI Note System",
            "version": "1.0.0", 
            "status": "running",
            "timestamp": datetime.now().isoformat(),
            "stats": {
                "total_notes": note_count,
                "database": "connected"
            },
            "endpoints": {
                "notes": "/api/notes",
                "chat": "/api/chat",
                "health": "/health"
            }
        })
        
    except Exception as e:
        return jsonify({
            "service": "🧠 AI Note System",
            "status": "error", 
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 500


@system_bp.route('/health')
def health_check():
    """헬스 체크"""
    try:
        # DB 연결 테스트
        db.session.execute(text('SELECT 1'))
        
        return jsonify({
            "status": "healthy",
            "database": "connected", 
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }), 503


@system_bp.route('/debug/routes')
def debug_routes():
    """등록된 라우트 확인 (디버깅용)"""
    try:
        routes = []
        for rule in current_app.url_map.iter_rules():
            if rule.endpoint != 'static':
                methods = [m for m in rule.methods if m not in ['HEAD', 'OPTIONS']]
                if methods:
                    routes.append({
                        'path': str(rule.rule),
                        'methods': methods,
                        'endpoint': rule.endpoint
                    })
        
        # 경로별 정렬
        routes.sort(key=lambda x: x['path'])
        
        return jsonify({
            "total_routes": len(routes),
            "routes": routes,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "라우트 정보 조회 실패",
            "details": str(e)
        }), 500


@system_bp.route('/debug/config')
def debug_config():
    """설정 정보 확인 (디버깅용)"""
    try:
        # 민감한 정보는 제외하고 출력
        safe_config = {}
        
        for key, value in current_app.config.items():
            # API 키나 비밀번호는 마스킹
            if any(sensitive in key.lower() for sensitive in ['key', 'password', 'secret']):
                if value:
                    safe_config[key] = f"{'*' * min(len(str(value)), 8)}..."
                else:
                    safe_config[key] = "Not Set"
            else:
                safe_config[key] = value
        
        return jsonify({
            "config": safe_config,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "설정 정보 조회 실패", 
            "details": str(e)
        }), 500


@system_bp.route('/debug/database')
def debug_database():
    """데이터베이스 상태 확인 (디버깅용)"""
    try:
        from models.note import Note
        
        # 기본 통계
        total_notes = Note.query.count()
        
        # 테이블 정보
        tables = db.engine.table_names()
        
        # 최근 노트 5개
        recent_notes = Note.query.order_by(Note.created_at.desc()).limit(5).all()
        
        return jsonify({
            "database_url": current_app.config.get('SQLALCHEMY_DATABASE_URI', '').split('://', 1)[0] + '://***',
            "tables": tables,
            "stats": {
                "total_notes": total_notes,
                "recent_notes": [
                    {
                        "id": note.id,
                        "title": note.title[:50] + "..." if len(note.title) > 50 else note.title,
                        "created_at": note.created_at.isoformat() if note.created_at else None
                    }
                    for note in recent_notes
                ]
            },
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "데이터베이스 정보 조회 실패",
            "details": str(e)
        }), 500


@system_bp.route('/debug/sample-notes', methods=['POST'])
def create_sample_notes():
    """샘플 노트 생성 (디버깅용)"""
    try:
        from models.note import Note
        
        # 기존 노트가 있으면 스킵
        if Note.query.count() > 0:
            return jsonify({
                "message": "이미 노트가 존재합니다",
                "existing_count": Note.query.count()
            })
        
        # 샘플 노트 데이터
        sample_notes = [
            {
                "title": "🎉 AI Note System 시작!",
                "content": """# AI Note System에 오신 것을 환영합니다!

## 주요 기능
- 📝 **마크다운 노트 작성**
- 🤖 **AI 채팅** (Claude 연동)
- 🔍 **노트 검색**
- 🏷️ **태그 시스템**

## 사용법
1. 새 노트 작성
2. 마크다운으로 내용 작성  
3. AI와 대화하며 노트 정리

시작해보세요! 🚀""",
                "tags": ["welcome", "getting-started"]
            },
            {
                "title": "📚 마크다운 사용법",
                "content": """# 마크다운 기본 문법

## 헤더
# 제목 1
## 제목 2  
### 제목 3

## 텍스트 스타일
**굵은 글씨**
*기울임*
~~취소선~~

## 리스트
- 항목 1
- 항목 2
  - 하위 항목

## 코드
`인라인 코드`

```python
# 코드 블록
def hello():
    print("Hello, World!")
```

## 링크 및 이미지
[링크 텍스트](https://example.com)

태그: #markdown #tutorial""",
                "tags": ["markdown", "tutorial", "syntax"]
            },
            {
                "title": "🤖 AI 채팅 테스트",
                "content": """# AI 채팅 기능 테스트

이 노트는 AI 채팅 기능을 테스트하기 위한 노트입니다.

## 테스트 질문들
- Vue.js에 대해 설명해주세요
- 파이썬 함수 작성법을 알려주세요  
- 마크다운 장점이 뭔가요?

## AI 응답 예시
AI가 이 노트의 내용을 참고해서 답변할 수 있습니다.

#ai #chatbot #test""",
                "tags": ["ai", "chatbot", "test"]
            }
        ]
        
        # 노트 생성
        created_notes = []
        for sample in sample_notes:
            note = Note(
                title=sample["title"],
                content=sample["content"]
            )
            note.set_tags(sample["tags"])
            db.session.add(note)
            created_notes.append(sample["title"])
        
        db.session.commit()
        
        return jsonify({
            "message": f"{len(created_notes)}개의 샘플 노트가 생성되었습니다",
            "created_notes": created_notes,
            "total_notes": Note.query.count()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            "error": "샘플 노트 생성 실패",
            "details": str(e)
        }), 500


@system_bp.route('/utils/markdown', methods=['POST'])
def markdown_preview():
    """마크다운 미리보기 (유틸리티)"""
    try:
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({"error": "마크다운 내용이 필요합니다"}), 400
        
        content = data['content']
        
        from utils.markdown_utils import process_markdown_content
        processed = process_markdown_content(content)
        
        return jsonify({
            "original": content,
            "processed": processed,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "마크다운 처리 실패",
            "details": str(e)
        }), 500


@system_bp.route('/utils/date-ranges', methods=['GET'])
def get_date_ranges():
    """사용 가능한 날짜 범위 목록"""
    try:
        from utils.date_utils import get_time_periods, get_date_range
        
        periods = get_time_periods()
        
        # 각 기간의 실제 날짜 범위 계산
        for period in periods:
            start, end = get_date_range(period['value'])
            period['start_date'] = start.isoformat()
            period['end_date'] = end.isoformat()
        
        return jsonify({
            "periods": periods,
            "current_time": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "날짜 범위 조회 실패",
            "details": str(e)
        }), 500


@system_bp.route('/utils/activity', methods=['GET'])
def get_activity_stats():
    """노트 작성 활동 통계"""
    try:
        from models.note import Note
        from utils.date_utils import get_activity_stats
        
        # 모든 노트 데이터
        notes = Note.query.all()
        note_data = []
        
        for note in notes:
            note_data.append({
                'id': note.id,
                'title': note.title,
                'created_at': note.created_at.isoformat() if note.created_at else None,
                'updated_at': note.updated_at.isoformat() if note.updated_at else None
            })
        
        # 활동 통계 계산
        stats = get_activity_stats(note_data)
        
        return jsonify({
            "activity_stats": stats,
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "활동 통계 조회 실패",
            "details": str(e)
        }), 500