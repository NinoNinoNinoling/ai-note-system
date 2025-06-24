# 🧠 AI Note System

**LangChain RAG와 Claude를 활용한 지능형 노트 시스템** - 과제 핵심 기능 구현! 🔥

## 📖 프로젝트 소개

이 프로젝트는 **LangChain RAG (Retrieval-Augmented Generation) 아키텍처**를 구현한 AI 노트 관리 시스템입니다. 마크다운 기반의 노트 작성과 벡터 검색을 통한 지능형 AI 채팅을 제공합니다.

### ✨ 핵심 기능 (과제 요구사항)

- 🔗 **LangChain RAG 구현** - 벡터 검색 + AI 생성 결합
- 📚 **FAISS 벡터 검색** - 노트 내용 임베딩 및 유사도 검색
- 🤖 **Claude AI 연동** - 컨텍스트 기반 지능형 응답
- 📝 **마크다운 노트** - 깔끔한 문서 작성 및 HTML 변환
- 🔍 **지능형 검색** - 텍스트 + 벡터 하이브리드 검색
- 🏷️ **태그 시스템** - 자동 태그 추출 및 분류
- 🔗 **노트 연결** - `[[링크]]` 문법으로 노트 간 연결
- 📊 **통계 및 분석** - 노트 현황, 인기 태그 등

## 🏗️ LangChain RAG 아키텍처

```
📝 노트 작성 → 🔤 텍스트 임베딩 → 🗂️ FAISS 벡터 저장
                                            ↓
🤖 AI 응답 ← 📚 컨텍스트 구성 ← 🔍 유사도 검색 ← 💬 사용자 질문
```

### 🔧 기술 스택 (LangChain 중심)

- **RAG Framework**: Custom RAG Implementation
- **Vector Store**: FAISS (Facebook AI Similarity Search)
- **Embeddings**: sentence-transformers (paraphrase-multilingual-MiniLM-L12-v2)
- **LLM**: Claude 3.5 Sonnet (Anthropic)
- **Backend**: Flask, SQLAlchemy, Blueprint 패턴
- **Database**: SQLite (개발용), 확장 가능
- **Language**: Python 3.8+

## 🚀 설치 및 실행

### 1. 프로젝트 클론
```bash
git clone <repository-url>
cd ai-note-system/backend
```

### 2. 가상환경 설정 (권장)
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux  
source venv/bin/activate
```

### 3. 의존성 설치
```bash
# 🔥 RAG 포함 전체 설치 (과제용 권장)
pip install -r requirements.txt

# 또는 개별 설치
pip install flask flask-sqlalchemy flask-cors python-dotenv anthropic python-dateutil faiss-cpu sentence-transformers numpy
```

### 4. 환경변수 설정
`.env` 파일을 생성하고 다음 내용 추가:
```env
SECRET_KEY=your-secret-key
FLASK_DEBUG=True
ANTHROPIC_API_KEY=sk-ant-your-api-key-here

# RAG 시스템 설정
RAG_INDEX_PATH=data/note_vectors.index
RAG_METADATA_PATH=data/notes_metadata.json
```

> **참고**: Claude API 키가 없어도 Mock 모드로 동작하며, RAG 검색 기능은 여전히 작동합니다.

### 5. 서버 실행
```bash
python run.py
```

서버가 성공적으로 시작되면 http://localhost:5000 에서 확인할 수 있습니다.

## 📚 API 엔드포인트

### 시스템 관리
- `GET /` - 시스템 상태 확인
- `GET /health` - 헬스 체크
- `POST /debug/sample-notes` - 샘플 노트 생성

### 노트 관리 (CRUD)
- `GET /api/notes` - 노트 목록 조회 (검색 지원)
- `POST /api/notes` - 새 노트 생성 (마크다운 처리)
- `GET /api/notes/<id>` - 특정 노트 조회 (관련 정보 포함)
- `PUT /api/notes/<id>` - 노트 수정
- `DELETE /api/notes/<id>` - 노트 삭제

### 고급 검색 및 분석
- `POST /api/notes/search` - 고급 검색 (하이라이트 포함)
- `GET /api/notes/suggest?q=검색어` - 검색 자동완성
- `GET /api/notes/<id>/similar` - 유사 노트 찾기
- `GET /api/notes/graph` - 노트 연결 그래프
- `GET /api/notes/stats` - 노트 통계

### 태그 관리
- `GET /api/notes/tags` - 태그 목록 (사용 횟수 포함)

### AI 채팅 (LangChain RAG 핵심!)
- `POST /api/chat` - 기본 AI 채팅
- `POST /api/chat/rag` - **🔥 RAG 기반 지능형 채팅 (과제 핵심!)**
- `GET /api/chat/test` - Claude API 연결 테스트
- `GET /api/chat/rag/status` - RAG 시스템 상태 확인
- `POST /api/chat/rag/rebuild` - RAG 인덱스 재구축

## 🎯 핵심 기능 상세

### 1. 마크다운 처리
노트는 풍부한 마크다운 기능을 지원합니다:

```markdown
# 제목
## 부제목

**굵은 글씨** *기울임* ~~취소선~~

- 리스트 항목
- 두 번째 항목

`인라인 코드`

[[다른 노트로 링크]]

#태그 #마크다운 #노트
```

### 2. 지능형 검색
- **텍스트 검색**: 제목, 내용에서 검색
- **태그 필터링**: 특정 태그로 필터링
- **검색 하이라이트**: 검색어 강조 표시
- **관련도 순 정렬**: 제목 매치 우선, 빈도 고려

### 3. 노트 연결 시스템
- **링크 생성**: `[[노트제목]]` 문법
- **백링크 추적**: 어떤 노트가 현재 노트를 링크하는지
- **연결 그래프**: 노트 간 관계 시각화 데이터

### 4. AI 채팅 (Mock/Real)
Claude API를 통한 AI 대화:

```json
{
  "message": "Vue.js에 대해 설명해주세요",
  "use_mock": false
}
```

## 🧪 테스트 방법

### 1. 시스템 상태 확인
```bash
curl http://localhost:5000/health
```

### 2. 샘플 노트 생성
```bash
curl -X POST http://localhost:5000/debug/sample-notes
```

### 3. 노트 생성 테스트
```bash
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "테스트 노트",
    "content": "# 안녕하세요\n\n이것은 **테스트** 노트입니다.\n\n#test #markdown",
    "tags": ["test", "demo"]
  }'
```

### 4. 검색 테스트
```bash
curl -X POST http://localhost:5000/api/notes/search \
  -H "Content-Type: application/json" \
  -d '{"query": "테스트"}'
```

### 5. AI RAG 채팅 테스트 (🔥 과제 핵심!)
```bash
# RAG 시스템 상태 확인
curl http://localhost:5000/api/chat/rag/status

# RAG 기반 지능형 채팅
curl -X POST http://localhost:5000/api/chat/rag \
  -H "Content-Type: application/json" \
  -d '{"message": "내 노트에서 LangChain에 대한 정보를 찾아줘"}'

# RAG 인덱스 재구축
curl -X POST http://localhost:5000/api/chat/rag/rebuild
```

### 6. 벡터 검색 테스트
```bash
# 노트 생성 (자동으로 RAG 인덱스에 추가됨)
curl -X POST http://localhost:5000/api/notes \
  -H "Content-Type: application/json" \
  -d '{
    "title": "LangChain RAG 구현",
    "content": "# LangChain RAG\n\nFAISS와 sentence-transformers를 사용한 벡터 검색 구현\n\n#langchain #rag #faiss",
    "tags": ["langchain", "rag", "ai"]
  }'
```

## 📁 프로젝트 구조

```
backend/
├── run.py                       # 🚀 앱 실행
├── app/
│   ├── __init__.py             # 🏭 Flask 앱 팩토리
│   └── routes/              
│       ├── system.py           # 🔧 시스템 & 디버깅
│       ├── notes.py            # 📝 노트 CRUD + 고급 기능
│       └── chat.py             # 🤖 AI 채팅
├── config/
│   ├── database.py             # 💾 DB 설정
│   └── settings.py             # ⚙️ 앱 설정
├── models/
│   └── note.py                 # 📊 노트 모델
├── utils/                      # 🛠️ 유틸리티들
│   ├── markdown_utils.py       # 마크다운 처리
│   ├── search_utils.py         # 검색 엔진
│   └── response_utils.py       # 응답 표준화
├── .env.example                # 환경변수 예시
└── requirements.txt            # 의존성
```

## 🎨 응답 형식

모든 API는 표준화된 응답 형식을 사용합니다:

```json
{
  "success": true,
  "message": "성공 메시지",
  "data": { ... },
  "timestamp": "2024-06-24T10:30:00"
}
```

오류 응답:
```json
{
  "success": false,
  "error": "오류 메시지",
  "details": "상세 정보",
  "timestamp": "2024-06-24T10:30:00"
}
```

## 🔧 개발 도구

### 디버깅 엔드포인트
- `/debug/routes` - 등록된 라우트 확인
- `/debug/config` - 설정 정보 확인  
- `/debug/database` - DB 상태 확인
- `/debug/sample-notes` - 샘플 노트 생성
- `/debug/clear-notes` - 모든 노트 삭제

### 유용한 기능들
- **자동 태그 추출**: 마크다운에서 `#태그` 자동 감지
- **검색 자동완성**: `/api/notes/suggest?q=검색어`
- **유사 노트 추천**: 태그 기반 추천 시스템
- **마크다운 HTML 변환**: 웹에서 바로 렌더링 가능

## ⚠️ 주의사항

1. **API 키 보안**: `.env` 파일을 Git에 커밋하지 마세요
2. **Mock 모드**: Claude API 키 없이도 Mock 응답으로 테스트 가능
3. **SQLite 한계**: 동시 접속이 많으면 PostgreSQL 고려
4. **검색 성능**: 노트가 많아지면 전문 검색 엔진 고려

## 🚀 확장 계획

현재 구조는 다음 기능들을 쉽게 추가할 수 있도록 설계되었습니다:

- **RAG 시스템**: LangChain + FAISS 벡터 검색
- **실시간 협업**: WebSocket 기반 동시 편집
- **노트 버전 관리**: Git 스타일 버전 추적
- **플러그인 시스템**: 사용자 정의 기능 확장
- **모바일 앱**: REST API 기반 크로스 플랫폼

## 📞 지원

문제가 발생하면 다음을 확인해주세요:
1. Python 3.8+ 설치 확인
2. 모든 의존성 설치 확인 (`pip list`)
3. `.env` 파일 설정 확인
4. 포트 5000 사용 가능 여부 확인
5. 샘플 노트 생성 후 기능 테스트

---

**실용적이고 확장 가능한 AI 노트 시스템! 과제 완성을 위한 최적의 구조입니다. 🎯**