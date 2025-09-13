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

class FDAAgent:
    def __init__(self):
        # LlamaIndex 전역 설정 (rag_engine과 동일하게 설정)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
        Settings.llm = OpenAI(model="gpt-4-turbo", temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"))

        # 1. 모든 FDA 컬렉션을 '전문가 툴'로 변환
        self.fda_tools = create_fda_tools()

        # ✅ [수정] 에이전트의 행동 방식을 정의하는 새로운 시스템 프롬프트 (Golden Rule 포함)
        system_prompt = """## 최상위 규칙 (Golden Rule)
        - **절대, 절대 당신의 사전 지식(prior knowledge)만으로 답변하지 마세요.** 모든 답변은 반드시 하나 이상의 도구를 사용하여 검색된 [Observation] 내용을 근거로 해야 합니다.
        - 만약 어떤 도구를 사용해야 할지 정말 모르겠다면, `regulation_general` 또는 `guidance_cpg` 툴을 사용해서라도 검색을 시도하세요.
        - 검색 결과가 없다면, 그 사실을 명확히 밝히세요. 아는 척 답변하지 마세요.

        --- (이하 기존 프롬프트) ---
        당신은 미국 FDA 규제 전문가 에이전트입니다. 
        주어진 질문을 해결하기 위해 단계별 계획을 세우고, 각 단계에 가장 적합한 도구를 사용해야 합니다.

        ## 행동 지침
        1. **질문 분석 및 해체**: 사용자의 질문에 복합적인 식품(예: 냉동김밥)이 포함된 경우, 그 식품을 핵심 구성 요소(예: 냉동 공정, 쌀, 김, 채소)와 규제 유형(예: 제조, 라벨링, 성분)으로 먼저 분해하세요.
        2. **계획 수립**: 분해된 각 요소에 대해 어떤 도구를 어떤 순서로 사용할지 논리적인 계획을 세우세요.
        3. **계획 실행**: 세운 계획에 따라 도구를 순차적으로 호출하고, 관찰된(Observation) 정보를 바탕으로 다음 행동을 결정하세요.
        4. **정보 종합 및 최종 답변**: 모든 도구에서 얻은 정보를 종합하여, 빠짐없이 일관성 있는 최종 답변을 생성하세요. 질문에 대한 직접적인 정보가 없는 경우, 각 구성 요소에 대한 규정을 종합하여 전문가로서 추론한 답변을 제공하고, 그 근거를 명확히 밝히세요.
        """

        # 2. ReAct 에이전트 생성
        self.agent = ReActAgent.from_tools(
            tools=self.fda_tools,
            llm=Settings.llm,
            system_prompt=system_prompt, # <--- 강화된 프롬프트 적용
            verbose=True  # 에이전트의 생각 과정을 로그로 확인
        )

    def chat(self, query: str) -> str:
        """
        사용자 질문에 대해 에이전트가 답변을 생성합니다.
        """
        response = self.agent.chat(query)
        return str(response)

    def stream_chat(self, query: str):
        """
        스트리밍 방식으로 답변을 생성합니다. (향후 확장 기능)
        """
        response_stream = self.agent.stream_chat(query)
        for token in response_stream.response_gen:
            yield token
