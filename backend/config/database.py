# backend/config/database.py - 과제용 개선 버전 (SQLAlchemy 2.0+ 호환)
"""
데이터베이스 설정 및 초기화

과제용으로 안정적이고 간단하게 구성 - SQLAlchemy 2.0+ 호환
"""

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text
import os

# 전역 DB 인스턴스
db = SQLAlchemy()


def init_db(app):
    """Flask 앱에 데이터베이스 초기화"""
    try:
        # SQLAlchemy 초기화
        db.init_app(app)
        
        # 앱 컨텍스트에서 테이블 생성
        with app.app_context():
            # 모든 모델 임포트 (테이블 생성을 위해)
            try:
                from models.note import Note
                print("✅ 노트 모델 로드 완료")
            except ImportError as e:
                print(f"⚠️ 모델 임포트 오류: {e}")
            
            # 데이터베이스 파일 확인
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI', '')
            if db_url.startswith('sqlite:///'):
                db_file = db_url.replace('sqlite:///', '')
                if os.path.exists(db_file):
                    print(f"📂 기존 데이터베이스 파일 발견: {db_file}")
                else:
                    print(f"📂 새 데이터베이스 파일 생성: {db_file}")
            
            # 모든 테이블 생성
            db.create_all()
            print("✅ 데이터베이스 테이블 생성 완료")
            
            # 테이블 확인
            check_tables()
            
    except Exception as e:
        print(f"❌ 데이터베이스 초기화 실패: {e}")
        raise


def check_tables():
    """생성된 테이블 확인 (SQLAlchemy 2.0+ 호환)"""
    try:
        # ✅ SQLAlchemy 2.0+ 호환 방식
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"📊 생성된 테이블: {', '.join(tables)}")
            
            # 노트 테이블 데이터 확인
            if 'notes' in tables:
                from models.note import Note
                note_count = Note.query.count()
                print(f"📝 기존 노트 수: {note_count}개")
        else:
            print("⚠️ 생성된 테이블이 없습니다")
            
    except Exception as e:
        print(f"⚠️ 테이블 확인 중 오류: {e}")


def get_db():
    """DB 인스턴스 반환 (다른 모듈에서 사용)"""
    return db


def reset_database():
    """데이터베이스 초기화 (개발용)"""
    try:
        print("🔄 데이터베이스 리셋 중...")
        
        # 모든 테이블 삭제
        db.drop_all()
        print("🗑️ 기존 테이블 삭제 완료")
        
        # 테이블 재생성
        db.create_all()
        print("✅ 테이블 재생성 완료")
        
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 리셋 실패: {e}")
        return False


def test_connection():
    """데이터베이스 연결 테스트"""
    try:
        # 간단한 쿼리 실행
        result = db.session.execute(text('SELECT 1'))
        result.fetchone()
        
        print("✅ 데이터베이스 연결 성공")
        return True
        
    except Exception as e:
        print(f"❌ 데이터베이스 연결 실패: {e}")
        return False


def get_db_info():
    """데이터베이스 정보 반환 (SQLAlchemy 2.0+ 호환)"""
    try:
        # ✅ SQLAlchemy 2.0+ 호환 방식
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        info = {
            "database_url": str(db.engine.url).replace('sqlite:///', 'sqlite:///...'),  # 보안상 경로 축약
            "driver": db.engine.url.drivername,
            "tables": tables,
            "connection_status": "connected"
        }
        
        # SQLite 파일 크기 확인
        if str(db.engine.url).startswith('sqlite:///'):
            db_file = str(db.engine.url).replace('sqlite:///', '')
            if os.path.exists(db_file):
                file_size = os.path.getsize(db_file)
                info["file_size_kb"] = round(file_size / 1024, 2)
            else:
                info["file_size_kb"] = 0
        
        return info
        
    except Exception as e:
        return {
            "connection_status": "error",
            "error": str(e)
        }


def backup_database(backup_path: str = None):
    """데이터베이스 백업 (SQLite용)"""
    try:
        if not str(db.engine.url).startswith('sqlite:///'):
            return False, "SQLite 데이터베이스만 백업 가능합니다"
        
        import shutil
        from datetime import datetime
        
        # 원본 파일 경로
        db_file = str(db.engine.url).replace('sqlite:///', '')
        
        if not os.path.exists(db_file):
            return False, "데이터베이스 파일이 존재하지 않습니다"
        
        # 백업 파일 경로
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"{db_file}.backup_{timestamp}"
        
        # 파일 복사
        shutil.copy2(db_file, backup_path)
        
        return True, f"백업 완료: {backup_path}"
        
    except Exception as e:
        return False, f"백업 실패: {str(e)}"


def create_sample_data():
    """샘플 데이터 생성 (테스트용)"""
    try:
        from models.note import Note
        
        # 기존 데이터 확인
        if Note.query.count() > 0:
            return False, "이미 데이터가 존재합니다"
        
        # 샘플 노트 생성
        sample_notes = [
            {
                "title": "🎉 AI Note System 시작!",
                "content": """# AI Note System에 오신 것을 환영합니다!

## 주요 기능
- 📝 **마크다운 노트 작성**
- 🤖 **AI 채팅** (Claude 연동)
- 🔍 **지능형 검색**
- 🏷️ **태그 시스템**

## 사용법
1. 새 노트 작성
2. 마크다운으로 내용 작성  
3. AI와 대화하며 노트 정리

시작해보세요! 🚀

#welcome #getting-started""",
                "tags": ["welcome", "getting-started"]
            },
            {
                "title": "📚 마크다운 기본 문법",
                "content": """# 마크다운 사용법

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

## 링크 및 노트 연결
[외부 링크](https://example.com)
[[다른 노트로 링크]]

## 태그
#markdown #tutorial #syntax""",
                "tags": ["markdown", "tutorial", "syntax"]
            },
            {
                "title": "🤖 AI 채팅 가이드",
                "content": """# AI 채팅 기능 활용법

## 기본 사용법
AI와 자연스럽게 대화하듯이 질문하세요.

## 유용한 질문 예시
- "Python 함수 작성법을 알려주세요"
- "Vue.js 컴포넌트에 대해 설명해주세요"
- "마크다운 문법을 정리해주세요"
- "프로젝트 구조 설계 방법은?"

## Mock 모드와 실제 모드
- **Mock 모드**: API 키 없이도 기본 응답 제공
- **실제 모드**: Claude API 키 설정시 고급 AI 응답

## 팁
- 구체적인 질문일수록 더 좋은 답변
- 예시를 들어 질문하면 더 정확한 답변
- 단계별로 나누어 질문하면 이해하기 쉬움

#ai #chatbot #guide #claude""",
                "tags": ["ai", "chatbot", "guide", "claude"]
            }
        ]
        
        # 노트 생성
        for sample in sample_notes:
            note = Note(
                title=sample["title"],
                content=sample["content"]
            )
            note.set_tags(sample["tags"])
            db.session.add(note)
        
        db.session.commit()
        
        return True, f"{len(sample_notes)}개의 샘플 노트가 생성되었습니다"
        
    except Exception as e:
        db.session.rollback()
        return False, f"샘플 데이터 생성 실패: {str(e)}"