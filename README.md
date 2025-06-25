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

* **Framework** : Flask (Python)
* **AI/ML** : LangChain + Claude API + sentence-transformers
* **Vector DB** : FAISS (Facebook AI Similarity Search)
* **Database** : SQLite (개발) / MySQL (프로덕션)
* **API** : RESTful API with comprehensive endpoints

### Frontend

* **Framework** : Vue.js 3 (Composition API)
* **State Management** : Pinia
* **Routing** : Vue Router
* **Styling** : Tailwind CSS
* **Editor** : Toast UI Editor (마크다운)
* **Testing** : Vitest + Vue Test Utils
* **Build Tool** : Vite
* **UI Components** : Lucide Vue (아이콘)

## 📁 프로젝트 구조

```
ai-note-system/
├── backend/                    # Flask API 서버
│   ├── app.py                 # 메인 애플리케이션
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
└── frontend/                   # Vue.js 웹 애플리케이션
    └── ai-note-frontend/      # Vue 프로젝트
        ├── public/            # 정적 파일
        ├── src/               # 소스 코드
        │   ├── assets/        # 에셋 (이미지, 스타일)
        │   ├── components/    # Vue 컴포넌트
        │   │   ├── common/    # 공통 컴포넌트
        │   │   ├── icons/     # 아이콘 컴포넌트
        │   │   ├── notes/     # 노트 관련 컴포넌트
        │   │   └── __tests__/ # 컴포넌트 테스트
        │   ├── router/        # Vue Router 설정
        │   ├── services/      # API 서비스
        │   ├── stores/        # Pinia 스토어
        │   ├── utils/         # 유틸리티 함수
        │   └── views/         # 페이지 컴포넌트
        ├── package.json       # 프론트엔드 의존성
        ├── vite.config.js     # Vite 설정
        ├── tailwind.config.js # Tailwind CSS 설정
        └── vitest.config.js   # 테스트 설정
```

## 🚀 실행 방법

### Backend 서버 실행

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Frontend 개발 서버

```bash
cd frontend/ai-note-frontend
npm install
npm run dev
```

### 테스트 실행

```bash
# Frontend 테스트
cd frontend/ai-note-frontend
npm run test
```

## 📚 API 엔드포인트

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

### 시스템

* `GET /` - 시스템 상태 및 기능 정보
* `GET /health` - 헬스 체크
* `GET /api/info` - API 문서

## 🔧 환경 설정

### Backend .env 파일

```
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///ai_notes.db
ANTHROPIC_API_KEY=sk-ant-your-claude-key
```

### Frontend 환경 변수 (선택사항)

```
VITE_API_BASE_URL=http://localhost:5000/api
```

## 🎯 개발 진행 상황

### ✅ Backend (완성)

* [X] 모듈화된 Flask 애플리케이션 구조
* [X] RAG 시스템 (sentence-transformers + FAISS)
* [X] Claude API 연동 및 AI 채팅
* [X] 노트 CRUD with 자동 벡터화
* [X] 태그 시스템 및 검색 기능
* [X] 채팅 히스토리 관리
* [X] 포괄적인 API 엔드포인트
* [X] 에러 처리 및 로깅

### 🔄 Frontend (진행 중)

* [X] Vue.js 3 + Vite 프로젝트 설정
* [X] 컴포넌트 구조 설계 (common, notes, icons)
* [X] Pinia 상태 관리 설정
* [X] Vue Router 라우팅 설정
* [X] Tailwind CSS 스타일링 설정
* [X] Vitest 테스트 환경 구성
* [X] Toast UI Editor 통합 준비
* [ ] 노트 목록/카드 컴포넌트 구현
* [ ] 마크다운 에디터 통합
* [ ] AI 채팅 인터페이스
* [ ] 검색 기능 UI
* [ ] 반응형 디자인

## 🏆 핵심 성과

1. **완전한 RAG 시스템** : 노트 기반 의미 검색 및 AI 응답
2. **모듈화 아키텍처** : 확장 가능하고 유지보수 쉬운 구조
3. **실용적 AI 통합** : Claude API와 LangChain 활용
4. **현대적 프론트엔드** : Vue 3 + Composition API + Tailwind
5. **포트폴리오급 품질** : 프로덕션 수준의 코드 구조

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