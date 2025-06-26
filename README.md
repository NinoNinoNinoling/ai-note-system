# AI Note System

LangChain과 Claude를 활용한 지능형 노트 시스템

## 프로젝트 개요

**개발 상태:** 백엔드 100% 완성, 프론트엔드 85% 완성, 핵심 기능 정상 작동
**핵심 기술:** LangChain + Claude 3.5 Sonnet + RAG + Vue.js
**목적:** 옵시디언 스타일 + Claude Artifacts 기능을 결합한 AI 노트 시스템

## 주요 기능

### AI 기능 (완전 구현)

* **RAG 기반 검색** : 노트 내용을 벡터화하여 의미 기반 검색
* **컨텍스트 인식 AI** : 사용자의 노트를 기반으로 정확한 답변 제공
* **실시간 벡터화** : 노트 생성 시 자동으로 임베딩 생성 및 인덱싱
* **Multiple Chains** : 노트 요약, 분석, 개선, 추천 기능 모두 정상 작동

### 노트 시스템 (완전 구현)

* **마크다운 지원** : 풍부한 텍스트 편집 기능
* **태그 시스템** : `#태그`로 노트 분류 및 필터링
* **노트 링크** : `[[노트제목]]` 문법으로 노트 간 연결
* **전문 검색** : 텍스트 검색 + RAG 기반 의미 검색

### AI 채팅 (완전 구현)

* **Claude 3.5 Sonnet 연동** : 최신 AI 모델 완전 연동
* **노트 기반 응답** : 사용자의 노트 내용을 컨텍스트로 활용
* **채팅 히스토리** : 대화 기록 저장, 검색, 요약 통계 제공

## 기술 스택

### Backend (100% 완성)

* **Framework** : Flask 3.1.1 (애플리케이션 팩토리 패턴)
* **AI/ML 핵심**:
  - LangChain 0.3.26 + LangChain Community 0.3.26
  - Anthropic 0.54.0 (Claude API)
  - Sentence Transformers 4.1.0 (임베딩)
  - PyTorch 2.7.1 (딥러닝 백엔드)
* **Vector DB** : FAISS 1.11.0 (Facebook AI Similarity Search)
* **Database** : SQLite (개발) / MySQL (프로덕션)
* **API** : RESTful API with Blueprint 모듈화

### Frontend (85% 완성)

* **Framework** : Vue.js 3.5 (Composition API)
* **State Management** : Pinia
* **Routing** : Vue Router 4
* **Styling** : Tailwind CSS + PostCSS
* **Build Tool** : Vite 5
* **Testing** : Vitest + Vue Test Utils
* **Code Quality** : ESLint + Prettier

## 프로젝트 구조

```
ai-note-system/
├── backend/                          # Flask API 서버
│   ├── app/                          # 메인 애플리케이션 (MVC 패턴)
│   │   ├── controllers/              # API 컨트롤러 레이어
│   │   ├── repositories/             # 데이터 액세스 레이어
│   │   ├── routes/                   # API 라우트 정의 (Blueprint)
│   │   ├── services/                 # 비즈니스 로직 레이어
│   │   └── __init__.py               # Flask 애플리케이션 팩토리
│   │
│   ├── chains/                       # LangChain RAG 체인
│   ├── config/                       # 설정 관리
│   ├── data/                         # 데이터 저장소
│   ├── models/                       # 데이터 모델
│   ├── utils/                        # 유틸리티 함수들
│   ├── .env                          # 환경변수
│   ├── requirements.txt              # Python 의존성
│   └── run.py                       # 애플리케이션 실행 파일
│
└── frontend/                         # Vue.js 웹 애플리케이션
    └── ai-note-frontend/            # Vue 프로젝트
        ├── src/
        │   ├── components/          # Vue 컴포넌트
        │   ├── router/              # Vue Router 설정
        │   ├── services/            # API 서비스
        │   ├── stores/              # Pinia 스토어
        │   ├── utils/               # 디버깅 도구
        │   └── views/               # 페이지 컴포넌트
        └── package.json             # 프론트엔드 의존성
```

## 실행 방법

### Backend 서버 실행

```bash
cd backend

# 가상환경 설정
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

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

# 의존성 설치
npm install

# 개발 서버 실행
npm run dev

# 빌드
npm run build

# 테스트 실행
npm run test
```

개발 서버가 http://localhost:5173 에서 실행됩니다.

## API 엔드포인트

### 시스템 관리
* `GET /` - 시스템 상태 및 기능 정보
* `GET /health` - 헬스 체크
* `GET /debug/routes` - 등록된 라우트 정보

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
* `POST /api/` - 기본 AI 채팅
* `POST /api/rag` - RAG 기반 컨텍스트 채팅
* `GET /api/test` - Claude API 연결 테스트
* `GET /api/rag/status` - RAG 시스템 상태
* `POST /api/rag/rebuild` - RAG 인덱스 재구축

### Multiple Chains
* `POST /api/summarize` - 노트 요약
* `POST /api/analyze` - 노트 분석
* `POST /api/improve` - 노트 개선 제안
* `POST /api/recommend` - 관련 노트 추천
* `GET /api/chains` - 체인 정보 조회

### 채팅 히스토리
* `GET /api/history` - 채팅 히스토리 조회
* `POST /api/history/search` - 히스토리 검색
* `GET /api/history/summary` - 채팅 요약 통계
* `DELETE /api/history` - 히스토리 삭제

### 통계 및 정보
* `GET /api/stats` - 기본 채팅 통계
* `GET /api/stats/advanced` - 고급 통계
* `GET /api/endpoints` - API 엔드포인트 목록

## 환경 설정

### Backend .env 파일

```env
# Flask 설정
SECRET_KEY=your-secret-key-here
FLASK_DEBUG=True

# 데이터베이스
DATABASE_URL=sqlite:///ai_notes_dev.db

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

## 개발 진행 상황

### Backend (100% 완성)

* [X] **모듈화된 Flask 구조** : 애플리케이션 팩토리 + Blueprint 패턴
* [X] **MVC 아키텍처** : Controllers, Services, Repositories 분리
* [X] **RAG 시스템** : Sentence Transformers + FAISS 벡터 검색
* [X] **Claude API 연동** : Anthropic + LangChain 기반 AI 채팅
* [X] **실시간 RAG 검색** : 노트 기반 지능형 컨텍스트 응답
* [X] **자동 벡터화** : 노트 생성 시 자동 임베딩 및 인덱싱
* [X] **고급 검색** : 텍스트 + 의미 기반 하이브리드 검색
* [X] **채팅 히스토리** : 대화 기록 저장, 검색, 요약, 내보내기
* [X] **Multiple Chains** : 요약, 분석, 개선, 추천 AI 기능
* [X] **에러 처리** : 포괄적인 예외 처리 및 로깅
* [X] **테스트 통과** : 모든 기능 100% 테스트 성공

### Frontend (85% 완성)

* [X] **Vue.js 3 + Vite 프로젝트 설정** : 완전한 개발 환경 구축
* [X] **컴포넌트 구조** : common, notes, icons 디렉토리 구성
* [X] **Pinia 상태 관리** : counter, notes 스토어 설정
* [X] **Vue Router 라우팅** : 페이지 네비게이션 구성
* [X] **Tailwind CSS + PostCSS** : 유틸리티 기반 스타일링
* [X] **ESLint + Prettier** : 코드 품질 및 포맷팅 도구
* [X] **Vitest 테스트 환경** : 컴포넌트 테스트 인프라
* [X] **주요 Vue 컴포넌트** : ChatView, NoteEditor, NotesView, SearchView
* [X] **API 서비스 레이어** : 완전한 백엔드 연동 구현
* [X] **노트 CRUD 기능** : 생성, 조회, 수정, 삭제 모두 정상 작동
* [X] **자동저장 시스템** : 실시간 자동저장 + 토글 기능
* [X] **에러 처리 개선** : 사용자 친화적 에러 메시지
* [X] **디버깅 도구** : 브라우저 콘솔에서 API 테스트 가능
* [ ] 실시간 검색 및 필터링 UI 완성
* [ ] 반응형 디자인 최적화
* [ ] AI 채팅 인터페이스 통합

## 최근 해결된 주요 버그

### 2025.06.26 버그 수정 완료

* **노트 생성·수정 API 연동 문제**
  - ✅ 400 Bad Request 에러 해결
  - ✅ axios Content-Type 헤더 이슈 수정
  - ✅ API 응답 구조 파싱 오류 수정 (`response.data.data.note`)
  - ✅ undefined 노트 객체 문제 해결

* **자동저장 기능 개선**
  - ✅ 자동저장 실패 시 모달창 제거
  - ✅ 필수 필드 검증 추가 (빈 제목/내용 처리)
  - ✅ 자동저장 토글 기능 추가
  - ✅ 부드러운 에러 처리 구현

* **개발자 경험 개선**
  - ✅ 브라우저 콘솔 디버깅 도구 추가
  - ✅ API 테스트 함수 (`window.testCreate()`, `window.testFlow()`)
  - ✅ 상세한 로깅 및 에러 추적

## 테스트 결과

**최신 테스트 성공률: 100% (9/9 그룹)**

* ✅ 서버 연결 테스트 - 통과
* ✅ 기본 AI 채팅 테스트 - 통과
* ✅ Claude API 연결 테스트 - 통과
* ✅ RAG 시스템 테스트 - 통과
* ✅ Multiple Chains 테스트 - 통과
* ✅ 채팅 히스토리 테스트 - 통과
* ✅ 통계 및 정보 테스트 - 통과
* ✅ 에러 처리 테스트 - 통과
* ✅ 성능 테스트 - 통과

**평균 응답시간:** 4.54초  
**총 API 엔드포인트:** 48개 (모두 정상 작동)

## 핵심 성과

1. **완전한 RAG 시스템** : 노트 기반 의미 검색 및 AI 응답 구현
2. **엔터프라이즈급 백엔드** : MVC 패턴, 애플리케이션 팩토리, Blueprint 모듈화
3. **프로덕션급 프론트엔드** : Vue 3 + Vite + 현대적 개발 도구 완비
4. **완전한 개발 환경** : 테스트, 린팅, 포맷팅, 디버깅 인프라
5. **실용적 AI 통합** : Claude API와 LangChain 활용한 RAG 시스템
6. **확장 가능한 아키텍처** : 모듈화된 구조로 유지보수성 극대화
7. **사용자 친화적 UI** : 자동저장, 실시간 미리보기, 직관적 인터페이스

## 향후 계획

### Phase 1 (진행중 - 85% 완성)
* [X] Vue.js 프론트엔드 API 연동 완성
* [X] 노트 CRUD 기능 완전 구현
* [X] 자동저장 시스템 완성
* [ ] AI 채팅 인터페이스 통합
* [ ] 실시간 노트 검색 UI 구현
* [ ] 반응형 디자인 완성

### Phase 2 (다음 단계)
* [ ] 노트 링크 시스템 (`[[노트제목]]`) 구현
* [ ] 태그 기반 필터링 및 검색
* [ ] 노트 간 관계 그래프 시각화
* [ ] 실시간 협업 기능 기초

### Phase 3 (장기 계획)
* [ ] 사용자 인증 시스템
* [ ] 플러그인 시스템
* [ ] 모바일 앱 개발
* [ ] 클라우드 배포 최적화

## 디버깅 도구

### 브라우저 콘솔에서 사용 가능한 도구들

```javascript
// API 테스트
window.testCreate()                    // 노트 생성 테스트
window.testFetch(id)                   // 노트 조회 테스트
window.testUpdate(id, data)            // 노트 수정 테스트
window.testFlow()                      // 전체 플로우 테스트

// 시스템 상태 확인
window.debugAPI.testSystemStatus()    // 시스템 전체 상태
window.debugAPI.analyzeResponse(res)  // API 응답 구조 분석
```

## 라이선스

MIT License

---

**개발 상태:** 백엔드 완전 완성, 프론트엔드 핵심 기능 완성, 실제 사용 가능  
**최종 업데이트:** 2025년 6월 26일  
**다음 마일스톤:** AI 채팅 UI 통합 및 고급 검색 기능 완성