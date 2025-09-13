# utils/agent.py
"""
ReAct 프레임워크를 사용하여 FDA 규제 질문에 답변하는 메인 에이전트.
"""
import os
from typing import List
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

from utils.tools import create_fda_tools
from utils.memory import ConversationMemory, ChatMessage

class FDAAgent:
    def __init__(self):
        # LlamaIndex 전역 설정 (rag_engine과 동일하게 설정)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
        Settings.llm = OpenAI(model="gpt-4-turbo", temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"))

        # 1. 모든 FDA 컬렉션을 '전문가 툴'로 변환
        self.fda_tools = create_fda_tools()

        # 멀티턴 대화를 위한 메모리 추가
        self.memory = ConversationMemory()

        # ✅ [수정] 에이전트의 행동 방식을 정의하는 새로운 시스템 프롬프트 (Golden Rule 포함)
        system_prompt = """## 최상위 규칙 (Golden Rule)
            - **절대, 절대 당신의 사전 지식(prior knowledge)만으로 답변하지 마세요.** 모든 답변은 반드시 하나 이상의 도구를 사용하여 검색된 [Observation] 내용을 근거로 해야 합니다.
            - **이전 대화 히스토리를 반드시 참조하세요.** "이 제품", "그것", "앞서 말한" 등의 표현이 나오면 이전 대화에서 언급된 구체적인 제품이나 주제를 찾아서 사용하세요.
            - **컨텍스트 연결 예시**: 이전에 "김치"에 대해 이야기했고 현재 "이 제품의 라벨링"이라고 하면, "김치의 라벨링"으로 이해해야 합니다.
            - 만약 어떤 도구를 사용해야 할지 정말 모르겠다면, `regulation_general` 또는 `guidance_cpg` 툴을 사용해서라도 검색을 시도하세요.
            - 검색 결과가 없다면, 그 사실을 명확히 밝히세요. 아는 척 답변하지 마세요.

            당신은 미국 FDA 규제 전문가 에이전트입니다. 
            주어진 질문을 해결하기 위해 단계별 계획을 세우고, 각 단계에 가장 적합한 도구를 사용해야 합니다.

            ## 행동 지침
            1. **컨텍스트 분석 우선**: 이전 대화 히스토리가 있다면, 현재 질문에서 대명사나 지시어("이", "그", "해당")가 무엇을 가리키는지 먼저 파악하세요.
            2. **질문 분석 및 해체**: 사용자의 질문에 복합적인 식품(예: 냉동김밥)이 포함된 경우, 그 식품을 핵심 구성 요소(예: 냉동 공정, 쌀, 김, 채소)와 규제 유형(예: 제조, 라벨링, 성분)으로 먼저 분해하세요.
            3. **계획 수립**: 분해된 각 요소에 대해 어떤 도구를 어떤 순서로 사용할지 논리적인 계획을 세우세요.
            4. **계획 실행**: 세운 계획에 따라 도구를 순차적으로 호출하고, 관찰된(Observation) 정보를 바탕으로 다음 행동을 결정하세요.
            5. **정보 종합 및 최종 답변**: 모든 도구에서 얻은 정보를 종합하여, 빠짐없이 일관성 있는 최종 답변을 생성하세요. 질문에 대한 직접적인 정보가 없는 경우, 각 구성 요소에 대한 규정을 종합하여 전문가로서 추론한 답변을 제공하고, 그 근거를 명확히 밝히세요.
            """

        # 2. ReAct 에이전트 생성
        self.agent = ReActAgent.from_tools(
            tools=self.fda_tools,
            llm=Settings.llm,
            system_prompt=system_prompt, # <--- 강화된 프롬프트 적용
            verbose=True  # 에이전트의 생각 과정을 로그로 확인
        )

    def chat(self, query: str) -> str:
        """멀티턴 대화를 지원하는 채팅 메서드"""
        # 이전 대화 컨텍스트와 함께 쿼리 구성
        context = self.memory.get_context_for_agent()
        full_query = f"{context}\n{query}" if context else query
        
        # 에이전트 응답 생성
        response = self.agent.chat(full_query)
        response_text = str(response)
        
        # 사용된 툴 추출 (에이전트의 source_nodes에서)
        used_tools = self._extract_used_tools(response)
        
        # 메모리에 대화 추가
        self.memory.add_message("user", query)
        self.memory.add_message("assistant", response_text, used_tools)
        
        return response_text
    
    def _extract_used_tools(self, response) -> List[str]:
        """응답에서 사용된 툴 목록을 추출"""
        used_tools = []
        if hasattr(response, 'source_nodes'):
            for node in response.source_nodes:
                if hasattr(node, 'metadata') and 'tool_name' in node.metadata:
                    tool_name = node.metadata['tool_name']
                    if tool_name not in used_tools:
                        used_tools.append(tool_name)
        return used_tools
    
    def reset_conversation(self):
        """대화 히스토리 초기화"""
        self.memory.clear_history()
        # 에이전트도 새로 시작
        self.agent.reset()


    ## 현재 사용되지 않아서 수정하지 않음. 
    def stream_chat(self, query: str):
        """
        스트리밍 방식으로 답변을 생성합니다. (향후 확장 기능)
        """
        response_stream = self.agent.stream_chat(query)
        for token in response_stream.response_gen:
            yield token
