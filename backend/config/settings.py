# backend/config/settings.py
import os
from dotenv import load_dotenv

# 환경변수 로드
load_dotenv()

class Config:
    """애플리케이션 설정 클래스"""
    
    # Flask 기본 설정
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-note-fallback-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # 데이터베이스 설정
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///ai_notes.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # AI API 설정
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # RAG 시스템 설정
    RAG_INDEX_PATH = os.getenv('RAG_INDEX_PATH', 'note_vectors.index')
    RAG_METADATA_PATH = os.getenv('RAG_METADATA_PATH', 'notes_metadata.json')
    
    @staticmethod
    def validate():
        """설정 검증"""
        missing = []
        
        if not Config.ANTHROPIC_API_KEY:
            missing.append('ANTHROPIC_API_KEY')
            
        if missing:
            print(f"⚠️ 누락된 환경변수: {', '.join(missing)}")
            print("💡 .env 파일을 확인해주세요")
            
        return len(missing) == 0
    
    @staticmethod
    def get_db_path():
        """SQLite DB 파일 절대 경로 반환"""
        if Config.SQLALCHEMY_DATABASE_URI.startswith('sqlite:///'):
            db_file = Config.SQLALCHEMY_DATABASE_URI.replace('sqlite:///', '')
            return os.path.abspath(db_file)
        return None