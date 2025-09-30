# PROJECT_FDA

FDA 식품 수출 규제 안내 시스템


## Overview

한국 중소기업이 미국으로 식품을 수출할 때 필요한 FDA 규제 정보를 제공하는 지능형 챗봇 시스템입니다. ReAct Agent를 활용하여 11개의 전문화된 FDA 문서 컬렉션에서 정확한 정보를 검색하고 제공합니다.

## Key Features

- **ReAct Agent**: 질문을 분석하여 적절한 전문가 툴을 자동 선택
- **Cross-Encoder Reranking**: 검색 품질 향상을 위한 재순위 알고리즘  
- **Tab-based UI**: 규제 확인, 인증서 분석, 서류 준비, 체크리스트 단계별 관리
- **한국 식품 특화**: 김치, 김밥 등 한국 고유 식품의 FDA 규제 대응

## Tech Stack

### Backend
- **FastAPI**: REST API 서버
- **LlamaIndex**: RAG 프레임워크 + ReAct Agent
- **Qdrant Cloud**: 벡터 데이터베이스 (11개 FDA 문서 컬렉션)
- **OpenAI**: GPT-4-turbo + text-embedding-3-small

### Frontend  
- **React**: 사용자 인터페이스
- **Tailwind CSS**: 스타일링
- **Lucide React**: 아이콘 라이브러리

### Development Tools
- **ChromaDB**: 로컬 문서 RAG 시스템 (개발자용)
- **Docker**: 컨테이너화된 배포

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
REACT_APP_API_URL=http://localhost:8000
```

## Project Structure

```
PROJECT_FDA/
├── backend/          # FastAPI server + ReAct Agent
├── frontend/         # React application  
├── docs/             # Project documentation
├── tools/rag/        # Developer documentation RAG system
└── docker-compose.yml
```

## Documentation

Comprehensive documentation is available in the `docs/` folder:

- **Architecture**: System overview and ReAct agent flow
- **Backend**: API endpoints and agent tools  
- **Frontend**: UI patterns and tab system
- **Development**: Coding standards and Git workflow
- **Deployment**: Docker setup and environment variables

For developer documentation access, use the RAG system in `tools/rag/`.

## Contributing

1. Clone the repository
2. Set up development environment (see Quick Start)
3. Check documentation in `docs/` folder or use RAG system
4. Follow Git workflow and coding standards as documented

## License

This project is licensed under the MIT License.
