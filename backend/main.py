from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv

from utils.qdrant_client import QdrantService
from utils.keyword_mapper import KeywordMapper

# 환경변수 로드
load_dotenv()

app = FastAPI(title="FDA Export Assistant API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
qdrant_service = QdrantService()
keyword_mapper = KeywordMapper()

# Request/Response 모델
class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None

class CFRReference(BaseModel):
    title: str
    description: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    keywords: List[str] = []
    cfr_references: List[CFRReference] = []
    sources: List[str] = []

@app.get("/")
async def root():
    return {"message": "FDA Export Assistant API"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        # 카테고리 매핑
        relevant_collections = keyword_mapper.get_relevant_collections(request.message)
        
        # Qdrant 검색
        search_results = await qdrant_service.search_multiple_collections(
            query=request.message,
            collections=relevant_collections,
            limit=5
        )
        
        # 응답 생성
        response = generate_response(request.message, search_results)
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

def generate_response(query: str, search_results: List) -> ChatResponse:
    """검색 결과를 바탕으로 응답 생성 (시뮬레이션)"""
    
    # 키워드 추출 (실제로는 더 정교한 로직 필요)
    keywords = extract_keywords(query)
    
    # CFR 참조 생성
    cfr_references = []
    sources = []
    
    for result in search_results[:3]:  # 상위 3개만 사용
        if result.payload.get('has_cfr'):
            cfr_references.append(CFRReference(
                title=result.payload.get('title', ''),
                description=f"관련 규제 문서입니다. 카테고리: {result.payload.get('category', '')}",
                url=result.payload.get('url', '')
            ))
        sources.append(result.payload.get('title', ''))
    
    # 기본 응답 생성
    if '김치' in query:
        content = "김치는 발효식품으로 분류되어 다음과 같은 FDA 규제를 확인해야 합니다. 검색된 관련 문서를 바탕으로 안내해드리겠습니다."
    else:
        content = f"'{query}'에 대한 FDA 규제 정보를 검색했습니다. 관련 문서 {len(search_results)}개를 찾았습니다."
    
    return ChatResponse(
        content=content,
        keywords=keywords,
        cfr_references=cfr_references,
        sources=sources
    )

def extract_keywords(query: str) -> List[str]:
    """쿼리에서 키워드 추출 (간단한 구현)"""
    keywords = []
    if '김치' in query:
        keywords.extend(['fermented', 'acidified', 'vegetable'])
    if '라면' in query:
        keywords.extend(['processed_grain', 'noodle', 'sodium'])
    if '수출' in query:
        keywords.extend(['export', 'import', 'regulation'])
    return keywords