# PROJECT_FDA🏛️

FDA 식품 수출 규제 안내 시스템

사용해보기: https://export-assistant.com/

## Overview

한국 식품기업이 미국 수출을 기획할 때 필요한 FDA 규제 정보를 제공하는 지능형 챗봇 시스템입니다. 
LlamaIndex 프레임워크를 기반으로 한 RAG를 통하여 **6개의 전문화된 FDA 문서 컬렉션**(GRAS, ECFR, DWPE, FSVP, Guidance, USC)에서 정확한 정보를 검색하고 제공합니다.
ReAct Agent 도입을 통해 복합식품에 대하여 보다 정확한 규제 정보를 제공합니다. 

## Key Features

- **ReAct Agent**: 질문을 분석하여 적절한 FDA 문서 컬렉션을 자동 선택
- **병렬 검색**: ThreadPoolExecutor를 활용한 다중 컬렉션 동시 검색으로 빠른 응답
- **프로젝트별 대화 관리**: 각 프로젝트마다 독립적인 대화 기록 유지
- **PWA 지원**: 모바일 앱처럼 설치 가능하며 오프라인 모드 지원
- **한국어 지원**: 한국어 질문을 영어로 자동 변환하여 검색
- **정확성 우선**: 정보가 없으면 솔직하게 인정하고 대안 제시

## Tech Stack

### Backend
- **FastAPI**: REST API 서버
- **LlamaIndex**: RAG 프레임워크 + ReAct Agent
- **Qdrant Cloud**: 벡터 데이터베이스 (6개 컬렉션)
- **OpenAI**: gpt-4o-mini (LLM) + text-embedding-3-small (임베딩)

### Frontend  
- **React**: 사용자 인터페이스
- **Tailwind CSS**: 스타일링
- **Lucide React**: 아이콘 라이브러리
- **PWA**: Service Worker를 통한 오프라인 지원

### Development Tools
- **ChromaDB**: 로컬 문서 RAG 시스템 (개발자용)
- **Docker**: 컨테이너화된 배포
- **Evaluation System**: 에이전트 성능 평가 도구 (backend/evaluation/)

## Quick Start

### Development Environment

1. **Frontend**
```bash
cd frontend
npm install
npm start  # http://localhost:3000
```

2. **Backend**
```bash
cd backend  
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8002 
```

3. **Developer Documentation RAG** (Optional)
```bash
cd tools/rag
setup.bat     # 초기 설정
start_work.bat  # 작업 시작
```

### Production Environment

```bash
docker-compose up --build
```

## Environment Variables

Create `.env` files in respective directories:

**Backend (.env):**
```bash
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333  
QDRANT_API_KEY=your_qdrant_api_key
```

**Frontend (.env):**
```bash
REACT_APP_API_URL=http://localhost:8002
```

## Project Structure

```
PROJECT_FDA_1021/
├── backend/          # FastAPI server + ReAct Agent
│   ├── main.py      # FastAPI 서버 및 API 엔드포인트
│   ├── utils/       # Agent, Tools, Memory, Orchestrator
│   └── evaluation/  # 에이전트 성능 평가 시스템
├── frontend/         # React application + PWA
│   ├── src/
│   │   ├── App.js   # 메인 컨테이너 (프로젝트 관리)
│   │   └── components/  # UI 컴포넌트
│   └── public/
│       ├── sw.js    # Service Worker (PWA)
│       └── manifest.json
├── docs/             # Project documentation
├── tools/rag/        # Developer documentation RAG system
└── docker-compose.yml
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **Architecture**: System overview and ReAct agent flow
- **Backend**: API endpoints and agent tools (6개 컬렉션 설명)
- **Frontend**: Component architecture and project management system
- **Development**: Coding standards and Git workflow
- **Deployment**: Docker setup and environment variables

For developer documentation access, use the RAG system in `tools/rag/`.

## FDA Document Collections

시스템에서 검색하는 6개의 FDA 문서 컬렉션:

1. **GRAS**: 식품 첨가물 안전성 승인 데이터베이스
2. **ECFR**: 21 CFR (연방 규정) - 제조 기준, HACCP 등
3. **DWPE**: Import Alert - 수입 거부 및 경고 정보
4. **FSVP**: 외국 공급업체 검증 프로그램 지침
5. **Guidance**: FDA 정책 해석 및 가이드라인
6. **USC**: 21 USC (미국 연방법) - 법적 정의 및 처벌 규정

## Contributing

1. Clone the repository
2. Set up development environment (see Quick Start)
3. Check documentation in `docs/` folder or use RAG system
4. Follow Git workflow and coding standards as documented

## License

This project is licensed under the MIT License.
