# backend/config/database.py
from flask_sqlalchemy import SQLAlchemy

# 전역 DB 인스턴스
db = SQLAlchemy()

def init_db(app):
    """Flask 앱에 데이터베이스 초기화"""
    db.init_app(app)
    
    with app.app_context():
        # 모든 테이블 생성
        db.create_all()
        print("✅ 데이터베이스 테이블 생성 완료")

def get_db():
    """DB 인스턴스 반환"""
    return db