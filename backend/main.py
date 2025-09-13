# main.py 수정 (기존 구조 보존)
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Optional
import os
from dotenv import load_dotenv
import logging

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

# [기존 유지] 기본 FDA Agent (fallback용)
try:
    fda_agent = FDAAgent()
    logger.info("FDA ReAct Agent initialized successfully.")
except Exception as e:
    logger.error(f"Failed to initialize FDA Agent: {e}")
    fda_agent = None

# [추가] 프로젝트별 에이전트 딕셔너리
project_agents: Dict[int, FDAAgent] = {}

class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None

class ChatResponse(BaseModel):
    content: str

@app.get("/")
async def root():
    return {"message": "FDA Export Assistant API - ReAct Agent"}

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not fda_agent:
        raise HTTPException(status_code=500, detail="Agent is not available.")
    
    try:
        project_id = request.project_id
        
        # 프로젝트 ID가 있으면 프로젝트별 에이전트 사용, 없으면 기본 에이전트 사용
        if project_id:
            if project_id not in project_agents:
                project_agents[project_id] = FDAAgent()
                logger.info(f"새 프로젝트 에이전트 생성: {project_id}")
            
            agent = project_agents[project_id]
            logger.info(f"프로젝트 {project_id}에서 질문 처리: {request.message}")
        else:
            # 기존 방식: 전역 에이전트 사용 (하위 호환성)
            agent = fda_agent
            logger.info(f"기본 에이전트로 질문 처리: {request.message}")
        
        agent_response = agent.chat(request.message)
        
        logger.info("Agent generated a response.")
        
        return ChatResponse(content=agent_response)
        
    except Exception as e:
        logger.error(f"Error processing agent chat request: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/project/{project_id}")
async def delete_project(project_id: int):
    """프로젝트 삭제 시 해당 에이전트도 제거"""
    if project_id in project_agents:
        del project_agents[project_id]
        logger.info(f"프로젝트 {project_id} 에이전트 삭제 완료")
    return {"message": "프로젝트가 삭제되었습니다."}

@app.post("/api/project/{project_id}/reset")
async def reset_project_conversation(project_id: int):
    """특정 프로젝트의 대화 히스토리 초기화"""
    if project_id in project_agents:
        project_agents[project_id].reset_conversation()
        logger.info(f"프로젝트 {project_id} 대화 히스토리 초기화 완료")
        return {"message": "대화 히스토리가 초기화되었습니다."}
    else:
        # 해당 프로젝트가 없으면 새로 생성
        project_agents[project_id] = FDAAgent()
        logger.info(f"프로젝트 {project_id} 새 에이전트 생성")
        return {"message": "새로운 대화가 시작되었습니다."}