# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import os
from dotenv import load_dotenv
import logging

# [수정] FDARAGEngine 대신 FDAAgent를 import
from utils.agent import FDAAgent

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="FDA Export Assistant API - ReAct Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# [수정] 서버 시작 시 FDAAgent 인스턴스를 하나만 생성
try:
    fda_agent = FDAAgent()
    logger.info("FDA ReAct Agent initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize FDA Agent: {e}")
    fda_agent = None

# Request/Response 모델 (기존과 동일하게 사용 가능)
class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    content: str
    # 에이전트 응답은 단순 텍스트이므로, 소스 등은 파싱이 필요할 수 있음
    # 우선은 content만 전달하도록 단순화
    
@app.get("/")
async def root():
    return {"message": "FDA Export Assistant API - ReAct Agent"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not fda_agent:
        raise HTTPException(status_code=500, detail="Agent is not available.")
    
    try:
        logger.info(f"Received query for agent: {request.message}")
        
        # [수정] KeywordMapper와 RAGEngine 호출 로직을 agent.chat() 하나로 대체
        agent_response = fda_agent.chat(request.message)
        
        logger.info("Agent generated a response.")
        
        return ChatResponse(content=agent_response)
        
    except Exception as e:
        logger.error(f"Error processing agent chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
 