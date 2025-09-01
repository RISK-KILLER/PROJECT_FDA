# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging

from utils.rag_engine import FDARAGEngine
from utils.keyword_mapper import KeywordMapper

# 환경변수 로드
load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FDA Export Assistant API")

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 서비스 초기화
rag_engine = FDARAGEngine()
keyword_mapper = KeywordMapper()

# Request/Response 모델
class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None
    include_checklist: Optional[bool] = True

class CFRReference(BaseModel):
    title: str
    description: str
    url: Optional[str] = None

class SourceDocument(BaseModel):
    title: str
    category: str
    url: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    keywords: List[str] = []
    cfr_references: List[CFRReference] = []
    sources: List[SourceDocument] = []

@app.get("/")
async def root():
    return {
        "message": "FDA Export Assistant API",
        "version": "2.0",
        "engine": "LlamaIndex RAG"
    }

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    try:
        # Qdrant 연결 테스트
        collections = rag_engine.qdrant_client.get_collections()
        return {
            "status": "healthy",
            "collections_count": len(collections.collections),
            "rag_engine": "active"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    메인 챗봇 엔드포인트
    FDA 규제 관련 질문에 대한 답변 생성
    """
    try:
        logger.info(f"Received query: {request.message}")
        
        # 1. KeywordMapper로 관련 컬렉션 식별
        relevant_collections = keyword_mapper.get_relevant_collections(request.message)
        
        # 2. 컬렉션이 없으면 기본 컬렉션 사용
        if not relevant_collections:
            relevant_collections = ['fda_ecfr', 'fda_general']
        
        logger.info(f"Selected collections: {relevant_collections}")
        
        # 3. RAG 엔진으로 검색 및 응답 생성
        response_data = rag_engine.query(
            query=request.message,
            collections=relevant_collections,
            include_checklist=request.include_checklist
        )
        
        # 4. 응답 포맷팅
        cfr_refs = [
            CFRReference(
                title=ref['title'],
                description=ref['description'],
                url=ref.get('url', '')
            )
            for ref in response_data.get('cfr_references', [])
        ]
        
        source_docs = [
            SourceDocument(
                title=src['title'],
                category=src.get('category', ''),
                url=src.get('url', '')
            )
            for src in response_data.get('sources', [])
        ]
        
        return ChatResponse(
            content=response_data['content'],
            keywords=response_data.get('keywords', []),
            cfr_references=cfr_refs,
            sources=source_docs
        )
        
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        
        # 에러 발생 시 기본 응답
        return ChatResponse(
            content=f"죄송합니다. 요청을 처리하는 중 오류가 발생했습니다. 다시 시도해 주세요.\n오류: {str(e)}",
            keywords=[],
            cfr_references=[],
            sources=[]
        )

@app.get("/api/collections")
async def list_collections():
    """사용 가능한 컬렉션 목록 반환"""
    try:
        collections = rag_engine.qdrant_client.get_collections()
        collection_info = []
        
        for collection in collections.collections:
            try:
                info = rag_engine.qdrant_client.get_collection(collection.name)
                collection_info.append({
                    "name": collection.name,
                    "vectors_count": info.points_count,
                    "category": collection.name.replace("fda_", "").replace("_", " ").title()
                })
            except:
                continue
        
        # 벡터 수 기준 정렬
        collection_info.sort(key=lambda x: x['vectors_count'], reverse=True)
        
        return {
            "total_collections": len(collection_info),
            "collections": collection_info[:10]  # 상위 10개만 반환
        }
        
    except Exception as e:
        logger.error(f"Error listing collections: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/test-query")
async def test_query(query: str = "김치 수출 시 필요한 FDA 규제는?"):
    """
    테스트용 쿼리 엔드포인트
    기본 질문으로 시스템 작동 확인
    """
    try:
        response_data = rag_engine.query(
            query=query,
            include_checklist=True
        )
        
        return {
            "query": query,
            "response": response_data['content'][:500] + "...",  # 처음 500자만
            "sources_count": len(response_data.get('sources', [])),
            "keywords": response_data.get('keywords', [])
        }
        
    except Exception as e:
        logger.error(f"Test query failed: {e}")
        return {
            "error": str(e),
            "status": "failed"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)