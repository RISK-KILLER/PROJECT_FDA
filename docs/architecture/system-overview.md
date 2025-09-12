## architecture/system-overview.md

```markdown
# System Overview

## 전체 구조
```
Frontend (React) → Backend (FastAPI) → ReAct Agent → Qdrant Vector DB
                                    ↓
                               11개 전문가 툴
                                    ↓
                            FDA 규제 문서 검색
```

## 핵심 컴포넌트

### Frontend
- **App.js**: 탭 시스템, 프로젝트 관리, 채팅 UI
- **API 통신**: /api/chat 엔드포인트로 질문 전송

### Backend  
- **main.py**: FastAPI 서버, 단일 chat 엔드포인트
- **Agent**: ReAct 프레임워크 기반 자율 판단
- **Tools**: 11개 FDA 문서 컬렉션별 전문가 툴

### Data Layer
- **Qdrant Cloud**: 벡터 DB (11개 컬렉션)
- **OpenAI**: 임베딩 + LLM (GPT-4-turbo)
- **Cross-Encoder Reranking**: 검색 품질 향상

## 정보 흐름
1. 사용자 질문 입력
2. Agent가 질문 분석
3. 적절한 툴(들) 자동 선택  
4. 벡터 검색 + 리랭킹
5. FDA 규제 정보 기반 답변 생성

## 핵심 특징
- **자율적 판단**: Agent가 스스로 툴 선택
- **한국 식품 특화**: 김치, 김밥 등 한국 식품 대응
- **정확성 우선**: 모르면 솔직하게 "모른다" 답변
```

이 정도로 **핵심 아키텍처와 데이터 흐름**만 명시하면, 새로 합류한 개발자나 Cursor AI가 전체 시스템을 빠르게 이해할 수 있습니다.