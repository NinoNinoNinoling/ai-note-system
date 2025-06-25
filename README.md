# 🧠 AI Note System

LangChain과 Claude를 활용한 지능형 노트 시스템

## 🎯 프로젝트 개요

**개발 기간:** 4일

**핵심 기술:** LangChain + Claude API + RAG(Retrieval-Augmented Generation)

**목적:** 옵시디언 스타일 + Claude Artifacts 기능을 결합한 AI 노트 시스템

## ✨ 주요 기능

### 🧠 AI 기능

* **RAG 기반 검색** : 노트 내용을 벡터화하여 의미 기반 검색
* **컨텍스트 인식 AI** : 사용자의 노트를 기반으로 정확한 답변 제공
* **실시간 벡터화** : 노트 생성 시 자동으로 임베딩 생성 및 인덱싱

### 📝 노트 시스템

* **마크다운 지원** : 풍부한 텍스트 편집 기능
* **태그 시스템** : `#태그`로 노트 분류 및 필터링
* **노트 링크** : `[[노트제목]]` 문법으로 노트 간 연결
* **전문 검색** : 텍스트 검색 + RAG 기반 의미 검색

### 💬 AI 채팅

* **Claude 3.5 Sonnet 연동** : 최신 AI 모델 활용
* **노트 기반 응답** : 사용자의 노트 내용을 컨텍스트로 활용
* **채팅 히스토리** : 대화 기록 저장 및 관리

## 🛠 기술 스택

### Backend

* **Framework** : Flask 3.1.1 (애플리케이션 팩토리 패턴)
* **AI/ML** : LangChain + Claude API + sentence-transformers
* **Vector DB** : FAISS (Facebook AI Similarity Search)
* **Database** : SQLite (개발) / MySQL (프로덕션)
* **API** : RESTful API with Blueprint 모듈화
* **의존성** : 25+ 최신 AI/ML 라이브러리

### Frontend

* **Framework** : Vue.js 3.5 (Composition API)
* **State Management** : Pinia (counter, notes 스토어)
* **Routing** : Vue Router 4
* **Styling** : Tailwind CSS + PostCSS
* **Build Tool** : Vite 5
* **Testing** : Vitest + Vue Test Utils
* **Code Quality** : ESLint + Prettier
* **Editor** : Toast UI Editor (통합 예정)
* **Icons** : Lucide Vue Next
* **Development** : 7000+ npm 패키지 의존성
* **HTTP Client** : Axios (API 통신)

## 📁 프로젝트 구조

```
ai-note-system/
├── backend/                          # Flask API 서버
│   ├── app/                          # 메인 애플리케이션 (MVC 패턴)
│   │   ├── controllers/              # API 컨트롤러 레이어
│   │   │   ├── base_controller.py
│   │   │   ├── chat_controller.py
│   │   │   ├── note_controller.py
│   │   │   └── __init__.py
│   │   ├── repositories/             # 데이터 액세스 레이어
│   │   │   ├── base_repository.py
│   │   │   ├── note_repository.py
│   │   │   └── __init__.py
│   │   ├── routes/                   # API 라우트 정의 (Blueprint)
│   │   │   ├── chat.py
│   │   │   ├── notes.py
│   │   │   ├── system.py
│   │   │   └── __init__.py
│   │   ├── services/                 # 비즈니스 로직 레이어
│   │   │   ├── chat_service.py
│   │   │   ├── note_service.py
│   │   │   └── __init__.py
│   │   └── __init__.py               # Flask 애플리케이션 팩토리
│   │
│   ├── chains/                       # LangChain RAG 체인
│   │   ├── rag_chain.py
│   │   └── __init__.py
│   │
│   ├── config/                       # 설정 관리
│   │   ├── database.py               # DB 설정 및 초기화
│   │   └── settings.py               # 환경변수 및 앱 설정
│   │
│   ├── data/                         # 데이터 저장소
│   │   ├── notes_metadata.json
│   │   ├── note_vectors.index
│   │   └── ai_notes.db
│   │
│   ├── models/                       # 데이터 모델
│   │   └── note.py                   # Note, ChatHistory 모델
│   │
│   ├── utils/                        # 유틸리티 함수들
│   │   ├── date_utils.py
│   │   ├── markdown_utils.py
│   │   ├── response_utils.py
│   │   └── search_utils.py
│   │
│   ├── venv/                         # Python 가상환경
│   ├── .env                          # 환경변수
│   ├── .env.example                  # 환경변수 템플릿
│   ├── ai_notes_dev.db              # 개발용 SQLite DB
│   ├── README.md                     # 백엔드 문서
│   ├── requirements.txt              # Python 의존성 (25+ 패키지)
│   └── run.py                       # 애플리케이션 실행 파일
│
└── frontend/                         # Vue.js 웹 애플리케이션
    └── ai-note-frontend/            # Vue 프로젝트
        ├── .vscode/                 # VS Code 설정
        ├── node_modules/            # npm 의존성 (7000+ 패키지)
        ├── public/                  # 정적 파일
        │   └── favicon.ico
        ├── src/                     # 소스 코드
        │   ├── assets/              # 에셋 (이미지, 스타일)
        │   │   ├── base.css
        │   │   ├── logo.svg
        │   │   └── main.css
        │   ├── components/          # Vue 컴포넌트
        │   │   ├── common/          # 공통 컴포넌트
        │   │   │   ├── HelloWorld.vue
        │   │   │   ├── TheWelcome.vue
        │   │   │   └── WelcomeItem.vue
        │   │   ├── icons/           # 아이콘 컴포넌트
        │   │   │   ├── IconCommunity.vue
        │   │   │   ├── IconDocumentation.vue
        │   │   │   ├── IconEcosystem.vue
        │   │   │   ├── IconSupport.vue
        │   │   │   └── IconTooling.vue
        │   │   ├── notes/           # 노트 관련 컴포넌트
        │   │   │   └── DeleteConfirmModal.vue
        │   │   └── __tests__/       # 컴포넌트 테스트
        │   │       └── HelloWorld.spec.js
        │   ├── router/              # Vue Router 설정
        │   │   └── index.js
        │   ├── services/            # API 서비스
        │   │   └── api.js
        │   ├── stores/              # Pinia 스토어
        │   │   ├── counter.js
        │   │   └── notes.js
        │   ├── utils/               # 유틸리티 함수
        │   ├── views/               # 페이지 컴포넌트
        │   │   ├── ChatView.vue
        │   │   ├── NoteEditor.vue
        │   │   ├── NotesView.vue
        │   │   ├── NotFound.vue
        │   │   └── SearchView.vue
        │   ├── App.vue              # 루트 컴포넌트
        │   ├── main.js              # 애플리케이션 엔트리 포인트
        │   └── style.css            # 글로벌 스타일
        ├── .editorconfig            # 에디터 설정
        ├── .gitattributes           # Git 속성
        ├── .gitignore               # Git 무시 파일
        ├── .prettierrc.json         # Prettier 설정
        ├── eslint.config.js         # ESLint 설정
        ├── index.html               # HTML 템플릿
        ├── jsconfig.json            # JavaScript 설정
        ├── package-lock.json        # 정확한 의존성 트리
        ├── package.json             # 프론트엔드 의존성
        ├── postcss.config.js        # PostCSS 설정
        ├── tailwind.config.js       # Tailwind CSS 설정
        ├── vite.config.js           # Vite 빌드 설정
        └── vitest.config.js         # Vitest 테스트 설정
```

## 🏗️ 백엔드 아키텍처

### MVC 패턴 구현
- **Controllers**: HTTP 요청 처리 및 응답 관리
- **Services**: 비즈니스 로직 처리
- **Repositories**: 데이터 액세스 추상화
- **Models**: SQLAlchemy ORM 모델

### Flask 애플리케이션 팩토리
- 모듈화된 앱 구조로 확장성과 테스트 용이성 확보
- Blueprint 기반 라우트 분리 (system, notes, chat)
- CORS 설정 및 미들웨어 통합

### 주요 의존성 라이브러리
```
LangChain 생태계: langchain, langchain-anthropic, langchain-community
AI/ML: anthropic, sentence-transformers, transformers, torch
Vector DB: faiss-cpu, numpy, scipy
Database: flask-sqlalchemy, mysql-connector-python
웹: flask, flask-cors, werkzeug
유틸리티: python-dotenv, python-dateutil, pyyaml
```

## 🚀 실행 방법

### Backend 서버 실행

```bash
cd backend

# 가상환경 설정 (권장)
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 환경변수 설정
cp .env.example .env
# .env 파일에 ANTHROPIC_API_KEY 등 설정

# 서버 실행
python run.py
```

서버가 http://localhost:5000 에서 실행됩니다.

### Frontend 개발 서버

```bash
cd frontend/ai-note-frontend

# 의존성 설치 (7000+ 패키지)
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 테스트 실행
npm run test
```

개발 서버가 http://localhost:5173 에서 실행됩니다.

### 테스트 실행

```bash
# Frontend 테스트
cd frontend/ai-note-frontend
npm run test

# Backend 테스트 (추후 구현 예정)
cd backend
python -m pytest
```

## 📚 API 엔드포인트

### 시스템 관리
* `GET /` - 시스템 상태 및 기능 정보
* `GET /health` - 헬스 체크

### 노트 관리

* `GET /api/notes` - 노트 목록 조회
* `POST /api/notes` - 노트 생성 (자동 RAG 인덱싱)
* `GET /api/notes/<id>` - 노트 상세 조회
* `PUT /api/notes/<id>` - 노트 수정
* `DELETE /api/notes/<id>` - 노트 삭제
* `POST /api/notes/search` - 텍스트 + RAG 검색
* `GET /api/notes/tags` - 태그 목록
* `GET /api/notes/stats` - 노트 통계

### AI 채팅

* `POST /api/chat` - 기본 AI 채팅
* `POST /api/chat/rag` - RAG 기반 컨텍스트 채팅
* `GET /api/chat/test` - Claude API 연결 테스트
* `GET /api/chat/history` - 채팅 기록 조회
* `POST /api/chat/rag/rebuild` - RAG 인덱스 재구축

## 🔧 환경 설정

### Backend .env 파일

```env
# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# 데이터베이스
DATABASE_URL=sqlite:///ai_notes.db

# Claude API
ANTHROPIC_API_KEY=sk-ant-your-claude-api-key

# RAG 시스템
RAG_INDEX_PATH=data/note_vectors.index
RAG_METADATA_PATH=data/notes_metadata.json
```

### Frontend 환경 변수

```env
VITE_API_BASE_URL=http://localhost:5000/api
```

## 🎯 개발 진행 상황

### ✅ Backend (완성)

* [X] **모듈화된 Flask 구조** : 애플리케이션 팩토리 + Blueprint 패턴
* [X] **MVC 아키텍처** : Controllers, Services, Repositories 분리
* [X] **RAG 시스템 완성** : sentence-transformers + FAISS 벡터 검색 ✅
* [X] **Claude API 연동** : LangChain 기반 AI 채팅 ✅
* [X] **실시간 RAG 검색** : 노트 기반 지능형 컨텍스트 응답 ✅
* [X] **자동 벡터화** : 노트 생성 시 자동 임베딩 및 인덱싱 ✅
* [X] **고급 검색** : 텍스트 + 의미 기반 하이브리드 검색
* [X] **채팅 히스토리** : 대화 기록 저장 및 관리
* [X] **에러 처리** : 포괄적인 예외 처리 및 로깅
* [X] **유틸리티** : 날짜, 마크다운, 응답, 검색 헬퍼 함수들
* [X] **RAG 인덱스 관리** : 재구축, 상태 확인, 통계 제공

### 🔄 Frontend (70% 완성)

* [X] **Vue.js 3 + Vite 프로젝트 설정** : 완전한 개발 환경 구축
* [X] **컴포넌트 구조** : common, notes, icons 디렉토리 구성
* [X] **Pinia 상태 관리** : counter, notes 스토어 설정
* [X] **Vue Router 라우팅** : 페이지 네비게이션 구성
* [X] **Tailwind CSS + PostCSS** : 유틸리티 기반 스타일링
* [X] **ESLint + Prettier** : 코드 품질 및 포맷팅 도구
* [X] **Vitest 테스트 환경** : 컴포넌트 테스트 인프라
* [X] **주요 Vue 컴포넌트** : 
  - ChatView, NoteEditor, NotesView, SearchView, NotFound
  - DeleteConfirmModal, 아이콘 컴포넌트들
* [X] **API 서비스 레이어** : 백엔드 연동 준비
* [ ] API 연동 및 데이터 흐름 구현
* [ ] Toast UI Editor 통합 완성
* [ ] 실시간 검색 및 필터링
* [ ] 반응형 디자인 최적화

## 🏆 핵심 성과

1. **완전한 RAG 시스템** : 노트 기반 의미 검색 및 AI 응답 구현
2. **엔터프라이즈급 백엔드** : MVC 패턴, 애플리케이션 팩토리, Blueprint 모듈화
3. **프로덕션급 프론트엔드** : Vue 3 + Vite + 7000+ 패키지 생태계
4. **완전한 개발 환경** : 테스트, 린팅, 포맷팅, 타입 검사 인프라
5. **실용적 AI 통합** : Claude API와 LangChain 활용한 RAG 시스템
6. **확장 가능한 아키텍처** : 모듈화된 구조로 유지보수성 극대화

## 📈 향후 계획

### Phase 1 (현재 진행)
* [ ] Vue.js 프론트엔드 UI 컴포넌트 완성
* [ ] API 연동 및 상태 관리
* [ ] 반응형 디자인 구현

### Phase 2 (다음 단계)
* [ ] 실시간 협업 기능
* [ ] 노트 버전 관리
* [ ] 고급 검색 및 필터링
* [ ] 사용자 인증 시스템

### Phase 3 (장기 계획)
* [ ] 플러그인 시스템
* [ ] 모바일 앱 개발
* [ ] 다중 사용자 지원
* [ ] 클라우드 배포

## 🛡 라이선스

MIT License

---

**개발자** : AI Note System Team  
**기술 문의** : 프로젝트 Issues 탭 활용  
**데모** : 개발 완료 후 링크 제공 예정