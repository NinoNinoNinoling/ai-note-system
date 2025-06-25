# AI Note System Backend

## 프로젝트 구조

```
ai-note-system/backend/
├── app/                          # 메인 애플리케이션
│   ├── controllers/              # API 컨트롤러
│   │   ├── base_controller.py
│   │   ├── chat_controller.py
│   │   ├── note_controller.py
│   │   └── __init__.py
│   ├── repositories/             # 데이터 액세스 레이어
│   │   ├── base_repository.py
│   │   ├── note_repository.py
│   │   └── __init__.py
│   ├── routes/                   # API 라우트 정의
│   │   ├── chat.py
│   │   ├── notes.py
│   │   ├── system.py
│   │   └── __init__.py
│   ├── services/                 # 비즈니스 로직
│   │   ├── chat_service.py
│   │   ├── note_service.py
│   │   └── __init__.py
│   └── __init__.py
├── chains/                       # LangChain RAG 체인
│   ├── rag_chain.py
│   └── __init__.py
├── config/                       # 설정 파일
│   ├── database.py
│   └── settings.py
├── data/                         # 데이터 저장소
│   ├── notes_metadata.json
│   ├── note_vectors.index
│   └── ai_notes.db
├── models/                       # 데이터 모델
│   └── note.py
├── utils/                        # 유틸리티 함수
│   ├── date_utils.py
│   ├── markdown_utils.py
│   ├── response_utils.py
│   └── search_utils.py
├── venv/                         # Python 가상환경
├── .env.example                  # 환경변수 템플릿
├── .env                          # 환경변수 (git ignore)
├── ai_notes_dev.db              # 개발용 SQLite DB
├── README.md                     # 프로젝트 문서
├── requirements.txt              # Python 의존성
└── run.py                       # 애플리케이션 실행 파일
```

## 주요 구성 요소

### 📁 app/
Flask 애플리케이션의 핵심 모듈들이 포함된 메인 디렉토리

- **controllers/**: HTTP 요청을 처리하는 컨트롤러 클래스들
- **repositories/**: 데이터베이스 접근을 담당하는 리포지토리 패턴 구현
- **routes/**: Flask 라우트 정의 및 엔드포인트 매핑
- **services/**: 비즈니스 로직을 처리하는 서비스 레이어

### 📁 chains/
LangChain을 활용한 RAG(Retrieval-Augmented Generation) 체인 구현

### 📁 config/
애플리케이션 설정 및 데이터베이스 연결 설정

### 📁 data/
노트 메타데이터, 벡터 인덱스, SQLite 데이터베이스 파일 저장

### 📁 models/
SQLAlchemy ORM 모델 정의

### 📁 utils/
날짜, 마크다운, 응답, 검색 관련 유틸리티 함수들

## 주요 기능

- 📝 **노트 관리**: CRUD 기능을 통한 노트 생성, 읽기, 수정, 삭제
- 🤖 **AI 채팅**: LangChain과 Anthropic Claude를 활용한 지능형 대화
- 🔍 **벡터 검색**: FAISS를 사용한 의미론적 노트 검색
- 📊 **SQLite 데이터베이스**: 경량화된 로컬 데이터 저장소

## 기술 스택

- **Framework**: Flask 3.1.1
- **AI/LLM**: LangChain, Anthropic Claude, OpenAI
- **Vector Store**: FAISS
- **Database**: SQLite with SQLAlchemy
- **Environment**: Python 3.11