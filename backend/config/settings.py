# backend/config/settings.py - 개선된 설정 관리
"""
애플리케이션 설정 관리

환경변수를 통한 설정 및 검증 기능 제공
"""

import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# 프로젝트 루트 디렉토리
BASE_DIR = Path(__file__).parent.parent

# 환경변수 파일 로드
env_file = BASE_DIR / '.env'
if env_file.exists():
    load_dotenv(env_file)
    print(f"✅ 환경변수 로드: {env_file}")
else:
    print(f"⚠️ .env 파일 없음: {env_file}")


class Config:
    """기본 설정 클래스"""
    
    # ========== Flask 기본 설정 ==========
    SECRET_KEY = os.getenv('SECRET_KEY', 'ai-note-fallback-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 'yes')
    TESTING = os.getenv('FLASK_TESTING', 'False').lower() in ('true', '1', 'yes')
    
    # ========== 데이터베이스 설정 ==========
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        f'sqlite:///{BASE_DIR / "ai_notes.db"}'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_timeout': 20,
        'pool_recycle': -1,
        'pool_pre_ping': True
    }
    
    # ========== AI API 설정 ==========
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # Claude 모델 설정
    CLAUDE_MODEL = os.getenv('CLAUDE_MODEL', 'claude-3-5-sonnet-20241022')
    CLAUDE_MAX_TOKENS = int(os.getenv('CLAUDE_MAX_TOKENS', '4000'))
    CLAUDE_TEMPERATURE = float(os.getenv('CLAUDE_TEMPERATURE', '0.7'))
    
    # ========== RAG 시스템 설정 ==========
    RAG_ENABLED = os.getenv('RAG_ENABLED', 'True').lower() in ('true', '1', 'yes')
    RAG_INDEX_PATH = os.getenv('RAG_INDEX_PATH', str(BASE_DIR / 'data' / 'note_vectors.index'))
    RAG_METADATA_PATH = os.getenv('RAG_METADATA_PATH', str(BASE_DIR / 'data' / 'notes_metadata.json'))
    RAG_EMBEDDING_MODEL = os.getenv('RAG_EMBEDDING_MODEL', 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')
    RAG_CHUNK_SIZE = int(os.getenv('RAG_CHUNK_SIZE', '500'))
    RAG_CHUNK_OVERLAP = int(os.getenv('RAG_CHUNK_OVERLAP', '50'))
    
    # ========== 보안 설정 ==========
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*').split(',')
    CORS_METHODS = os.getenv('CORS_METHODS', 'GET,POST,PUT,DELETE,OPTIONS').split(',')
    CORS_HEADERS = os.getenv('CORS_HEADERS', 'Content-Type,Authorization').split(',')
    
    # ========== 파일 업로드 설정 ==========
    MAX_CONTENT_LENGTH = int(os.getenv('MAX_CONTENT_LENGTH', '16777216'))  # 16MB
    UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))
    ALLOWED_EXTENSIONS = set(os.getenv('ALLOWED_EXTENSIONS', 'md,txt,json').split(','))
    
    # ========== 로깅 설정 ==========
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'app.log'))
    
    # ========== 캐싱 설정 ==========
    CACHE_TYPE = os.getenv('CACHE_TYPE', 'simple')
    CACHE_DEFAULT_TIMEOUT = int(os.getenv('CACHE_DEFAULT_TIMEOUT', '300'))
    
    # ========== 속도 제한 설정 ==========
    RATELIMIT_ENABLED = os.getenv('RATELIMIT_ENABLED', 'False').lower() in ('true', '1', 'yes')
    RATELIMIT_DEFAULT = os.getenv('RATELIMIT_DEFAULT', '100 per hour')
    RATELIMIT_STORAGE_URL = os.getenv('RATELIMIT_STORAGE_URL', 'memory://')
    
    @classmethod
    def validate(cls) -> bool:
        """설정 유효성 검사"""
        missing_vars = []
        warnings = []
        
        # 필수 환경변수 체크
        required_vars = []
        
        for var in required_vars:
            if not getattr(cls, var, None):
                missing_vars.append(var)
        
        # 권장 환경변수 체크
        if not cls.ANTHROPIC_API_KEY:
            warnings.append('ANTHROPIC_API_KEY가 설정되지 않음 - Claude AI 기능 사용 불가')
        
        if cls.SECRET_KEY == 'ai-note-fallback-secret-key-change-in-production':
            warnings.append('기본 SECRET_KEY 사용 중 - 프로덕션에서는 변경 필요')
        
        # 디렉토리 생성
        cls._create_directories()
        
        # 결과 출력
        if missing_vars:
            print(f"❌ 필수 환경변수 누락: {', '.join(missing_vars)}")
            return False
        
        if warnings:
            print("⚠️ 설정 경고:")
            for warning in warnings:
                print(f"   - {warning}")
        
        print("✅ 설정 검증 완료")
        return True
    
    @classmethod
    def _create_directories(cls):
        """필요한 디렉토리 생성"""
        directories = [
            Path(cls.UPLOAD_FOLDER),
            Path(cls.RAG_INDEX_PATH).parent,
            Path(cls.LOG_FILE).parent
        ]
        
        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def get_database_url(cls) -> str:
        """데이터베이스 URL 반환"""
        return cls.SQLALCHEMY_DATABASE_URI
    
    @classmethod
    def get_rag_config(cls) -> dict:
        """RAG 시스템 설정 반환"""
        return {
            'enabled': cls.RAG_ENABLED,
            'index_path': cls.RAG_INDEX_PATH,
            'metadata_path': cls.RAG_METADATA_PATH,
            'embedding_model': cls.RAG_EMBEDDING_MODEL,
            'chunk_size': cls.RAG_CHUNK_SIZE,
            'chunk_overlap': cls.RAG_CHUNK_OVERLAP
        }
    
    @classmethod
    def get_claude_config(cls) -> dict:
        """Claude API 설정 반환"""
        return {
            'api_key': cls.ANTHROPIC_API_KEY,
            'model': cls.CLAUDE_MODEL,
            'max_tokens': cls.CLAUDE_MAX_TOKENS,
            'temperature': cls.CLAUDE_TEMPERATURE
        }
    
    @classmethod
    def get_cors_config(cls) -> dict:
        """CORS 설정 반환"""
        return {
            'origins': cls.CORS_ORIGINS,
            'methods': cls.CORS_METHODS,
            'allow_headers': cls.CORS_HEADERS
        }


class DevelopmentConfig(Config):
    """개발 환경 설정"""
    DEBUG = True
    TESTING = False
    
    # 개발용 데이터베이스
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DEV_DATABASE_URL',
        f'sqlite:///{BASE_DIR / "ai_notes_dev.db"}'
    )
    
    # 더 상세한 로깅
    LOG_LEVEL = 'DEBUG'
    
    # RAG 시스템 테스트용 설정
    RAG_CHUNK_SIZE = 300
    RAG_CHUNK_OVERLAP = 30


class TestingConfig(Config):
    """테스트 환경 설정"""
    TESTING = True
    DEBUG = True
    
    # 메모리 데이터베이스
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    
    # 테스트용 설정
    WTF_CSRF_ENABLED = False
    RAG_ENABLED = False
    
    # 테스트용 API 키 (Mock)
    ANTHROPIC_API_KEY = 'test-key'


class ProductionConfig(Config):
    """프로덕션 환경 설정"""
    DEBUG = False
    TESTING = False
    
    # 프로덕션 데이터베이스 (PostgreSQL 권장)
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'PROD_DATABASE_URL',
        'postgresql://user:password@localhost/ai_notes_prod'
    )
    
    # 보안 강화
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # 성능 최적화
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 20,
        'pool_timeout': 30,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
        'max_overflow': 30
    }
    
    # 속도 제한 활성화
    RATELIMIT_ENABLED = True
    
    # 에러 로깅
    LOG_LEVEL = 'WARNING'


# 환경별 설정 매핑
config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(config_name: Optional[str] = None) -> Config:
    """
    설정 클래스 반환
    
    Args:
        config_name: 설정 이름 ('development', 'testing', 'production')
    
    Returns:
        설정 클래스
    """
    if config_name is None:
        config_name = os.getenv('FLASK_CONFIG', 'default')
    
    return config.get(config_name, DevelopmentConfig)


def print_config_summary(config_obj: Config):
    """설정 요약 출력"""
    print("\n" + "=" * 50)
    print("⚙️ Configuration Summary")
    print("=" * 50)
    
    print(f"Environment: {config_obj.__class__.__name__}")
    print(f"Debug Mode: {config_obj.DEBUG}")
    print(f"Database: {config_obj.get_database_url()}")
    print(f"RAG Enabled: {config_obj.RAG_ENABLED}")
    print(f"Claude API: {'✅' if config_obj.ANTHROPIC_API_KEY else '❌'}")
    print(f"Log Level: {config_obj.LOG_LEVEL}")
    
    print("=" * 50 + "\n")


# 기본 설정 인스턴스 (하위 호환성)
Config = get_config()