# 🧠 AI Note System

LangChain과 Claude를 활용한 지능형 노트 시스템

## 📁 프로젝트 구조

```
ai-note-system/
├── backend/
│   ├── app.py                 # 메인 애플리케이션 (리팩토링됨!)
│   ├── requirements.txt       # Python 의존성
│   ├── .env                   # 환경변수
│   │
│   ├── config/                # 설정 관리
│   │   ├── database.py        # DB 설정 및 초기화
│   │   └── settings.py        # 환경변수 및 앱 설정
│   │
│   ├── models/                # 데이터 모델
│   │   └── note.py            # Note, ChatHistory 모델
│   │
│   ├── app/                   # Flask 애플리케이션
│   │   ├── __init__.py
│   │   └── routes/            # API 라우트
│   │       ├── __init__.py
│   │       ├── notes.py       # 노트 CRUD API
│   │       └── chat.py        # AI 채팅 API
│   │
│   ├── chains/                # LangChain 체인들
│   │   └── rag_chain.py       # RAG 시스템
│   │
│   └── utils/                 # 유틸리티 함수들
│       └── markdown_parser.py # 마크다운 처리
│
├── frontend/                  # (향후 개발 예정)
└── README.md
```

## 🚀 실행 방법

### 1. 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2. 환경변수 설정

`.env` 파일에 다음 내용 추가:

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ai_notes.db
ANTHROPIC_API_KEY=sk-ant-your-claude-key
```

### 3. 서버 실행

```bash
python app.py
```

## 📚 API 엔드포인트

### 노트 관리

* `GET /api/notes` - 노트 목록
* `POST /api/notes` - 노트 생성
* `GET /api/notes/<id>` - 노트 상세
* `PUT /api/notes/<id>` - 노트 수정
* `DELETE /api/notes/<id>` - 노트 삭제
* `POST /api/notes/search` - 노트 검색
* `GET /api/notes/tags` - 태그 목록

### AI 채팅

* `POST /api/chat` - 기본 AI 채팅
* `POST /api/chat/rag` - RAG 기반 채팅
* `GET /api/chat/test` - Claude API 테스트
* `POST /api/chat/rag/rebuild` - RAG 인덱스 재구축

### 시스템

* `GET /` - 시스템 상태
* `GET /health` - 헬스 체크
* `GET /api/info` - API 정보

## 🔧 주요 기능

### 1. 노트 시스템

* ✅ CRUD 연산
* ✅ 태그 시스템 (#태그)
* ✅ 노트 링크 ([[링크]])
* ✅ 마크다운 지원
* ✅ 검색 기능

### 2. RAG (Retrieval-Augmented Generation)

* ✅ sentence-transformers로 벡터화
* ✅ FAISS 벡터 검색
* ✅ 유사 노트 찾기
* ✅ 컨텍스트 기반 AI 응답

### 3. AI 채팅

* ✅ Claude 3.5 Sonnet 연동
* ✅ 노트 기반 질의응답
* ✅ 채팅 기록 저장
* ✅ Mock 응답 (개발용)

## 🛠 기술 스택

### Backend

* **Framework** : Flask
* **Database** : SQLite (개발), MySQL (프로덕션)
* **AI/ML** : LangChain + Claude API
* **Vector DB** : FAISS
* **Embeddings** : sentence-transformers

### AI 모델

* **LLM** : Claude 3.5 Sonnet
* **Embeddings** : paraphrase-multilingual-MiniLM-L12-v2
* **Vector Search** : FAISS (Facebook AI Similarity Search)

## 📈 향후 계획

### Phase 1 (현재)

* ✅ 기본 노트 CRUD
* ✅ RAG 시스템
* ✅ AI 채팅

### Phase 2 (다음)

* [ ] Vue.js 프론트엔드
* [ ] 실시간 협업
* [ ] 고급 검색
* [ ] 노트 버전 관리

### Phase 3 (미래)

* [ ] 플러그인 시스템
* [ ] 모바일 앱
* [ ] 다중 사용자
* [ ] 클라우드 배포

## 🎯 프로젝트 특징

1. **모듈화된 구조** : 기능별로 깔끔하게 분리
2. **확장 가능** : 새로운 AI 모델 쉽게 추가 가능
3. **실용적** : 실제 사용 가능한 노트 시스템
4. **교육적** : LangChain 학습에 최적화

## 📝 개발 노트

이 프로젝트는 LangChain의 핵심 개념들을 실제 애플리케이션에 적용한 예시입니다:

* **Chains** : 여러 AI 작업을 연결
* **RAG** : 문서 검색과 생성 결합
* **Memory** : 대화 맥락 유지
* **Embeddings** : 의미 기반 검색
