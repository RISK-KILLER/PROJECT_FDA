# utils/memory.py
"""
멀티턴 대화를 위한 메모리 매니저
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class ChatMessage:
    """단일 채팅 메시지를 나타내는 클래스"""
    role: str  # 'user' 또는 'assistant'
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    tools_used: List[str] = field(default_factory=list)  # 사용된 툴 목록

class ConversationMemory:
    """대화 히스토리를 관리하는 클래스"""
    
    def __init__(self, max_history: int = 10):
        self.messages: List[ChatMessage] = []
        self.max_history = max_history
    
    def add_message(self, role: str, content: str, tools_used: List[str] = None):
        """새 메시지를 히스토리에 추가"""
        message = ChatMessage(
            role=role, 
            content=content, 
            tools_used=tools_used or []
        )
        self.messages.append(message)
        
        # 최대 히스토리 개수 제한
        if len(self.messages) > self.max_history * 2:  # user + assistant 쌍
            self.messages = self.messages[-self.max_history * 2:]
    
    def get_context_for_agent(self) -> str:
        """에이전트에게 전달할 컨텍스트 문자열 생성"""
        if not self.messages:
            return ""
        
        context_parts = ["## 이전 대화 요약:"]
        
        # 최근 대화에서 주요 제품/주제 추출
        recent_topics = []
        for msg in self.messages[-6:]:  # 최근 3턴
            if msg.role == "user":
                # 제품명이나 주요 키워드 추출 (간단한 패턴)
                content_lower = msg.content.lower()
                if "김치" in content_lower:
                    recent_topics.append("김치")
                elif "만두" in content_lower:
                    recent_topics.append("만두")
                # 필요시 더 많은 제품 추가
        
        if recent_topics:
            context_parts.append(f"**주요 논의 제품**: {', '.join(set(recent_topics))}")
        
        context_parts.append("\n## 최근 대화 내역:")
        for msg in self.messages[-4:]:  # 최근 2턴만 포함
            role_kr = "사용자" if msg.role == "user" else "어시스턴트"
            context_parts.append(f"**{role_kr}**: {msg.content}")
        
        context_parts.append("\n## 현재 질문:")
        return "\n".join(context_parts)
    
    def clear_history(self):
        """대화 히스토리 초기화"""
        self.messages.clear()