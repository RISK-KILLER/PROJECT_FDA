# System Overview

## 전체 구조
```
Frontend (React) → Backend (FastAPI) → ReAct Agent → Qdrant Vector DB
                                    ↓
                            6개 FDA 문서 컬렉션
                                    ↓
                            벡터 검색 + LLM 답변
```

## 핵심 컴포넌트

### Frontend
- **App.js**: 프로젝트 관리, 채팅 UI, PWA 기능
- **Components**: MessageList, InputBar, Sidebar, HelpModal, Citation 관련 컴포넌트 등
- **API 통신**: /api/chat 엔드포인트로 질문 전송

### Backend  
- **main.py**: FastAPI 서버, chat/project 관리 엔드포인트
- **agent.py**: ReAct 프레임워크 기반 자율 판단 에이전트
- **tools.py**: 6개 FDA 문서 컬렉션별 검색 툴 (GRAS, ECFR, DWPE, FSVP, Guidance, USC)
- **orchestrator.py**: 에이전트 오케스트레이션
- **memory.py**: 대화 기록 관리
- **collection_strategy.py**: 컬렉션 선택 전략
- **qdrant_client.py**: Qdrant DB 클라이언트

### Data Layer
- **Qdrant Cloud**: 벡터 DB (7개 컬렉션)
- **OpenAI**: 임베딩(text-embedding-3-small) + LLM (gpt-4o-mini)
- **벡터 검색**: similarity_top_k=5

## 정보 흐름
1. 사용자 질문 입력
2. Agent가 질문 분석 및 적절한 컬렉션 자동 선택
3. 벡터 검색 실행
4. FDA 규제 정보 기반 답변 생성
5. 프론트엔드에 응답 반환 (citations 포함)

## 핵심 특징
- **프로젝트별 대화 관리**: 각 프로젝트마다 독립적인 대화 기록 유지
- **자율적 판단**: Agent가 스스로 적절한 컬렉션 선택
- **한국어 지원**: 한국어 질문을 영어로 변환하여 검색
- **PWA 지원**: 모바일 앱처럼 설치 가능
- **정확성 우선**: 모르면 솔직하게 "모른다" 답변