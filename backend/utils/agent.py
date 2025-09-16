# utils/agent.py
"""
ReAct 프레임워크를 사용하여 FDA 규제 질문에 답변하는 메인 에이전트.
"""
import os
import json
import re
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
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-ada-002", api_key=os.getenv("OPENAI_API_KEY"))
        Settings.llm = OpenAI(model="gpt-4-turbo", temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"))

        # 1. 모든 FDA 컬렉션을 '전문가 툴'로 변환
        self.fda_tools = create_fda_tools()

        # 멀티턴 대화를 위한 메모리 추가
        self.memory = ConversationMemory()
        
        # 제품 분해 캐시 추가
        self.decomposition_cache = {}

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
            max_iterations=10,  # 추가: 최대 반복 횟수 증가
            verbose=True  # 에이전트의 생각 과정을 로그로 확인
        )

    def _is_food_export_question_llm(self, query: str) -> bool:
        """
        빠르고 저렴한 LLM(gpt-3.5-turbo)을 사용하여 사용자의 질문이
        '특정 식품의 수출 규제'에 대한 것인지 분류하는 필터 함수.
        """
        try:
            # 필터 전용으로 저렴한 모델을 임시로 사용
            filter_llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
            
            prompt = f"""
            Is the following user query about the regulations for exporting a specific food item?
            Answer ONLY with "Yes" or "No". Do not add any other text, explanation, or punctuation.

            Query: "{query}"
            """
            
            response = filter_llm.complete(prompt)
            answer = response.text.strip().lower()
            
            print(f"LLM Filter Check for query '{query}': Answer='{answer}'") # 디버깅용 로그
            
            return answer == "yes"

        except Exception as e:
            print(f"LLM Filter failed: {e}") # 에러 로그
            return False # 에러 발생 시 안전하게 False로 처리

    def _decompose_product(self, product_name: str) -> dict:
        """LLM을 사용한 제품 분해"""
        # 캐시 확인
        if product_name in self.decomposition_cache:
            return self.decomposition_cache[product_name]
        
        decomposition_prompt = f"""
        Analyze the food product '{product_name}' for FDA export requirements.
        
        Return a JSON object with these exact keys:
        - ingredients: list of main components in English (e.g., ["shrimp", "wheat flour", "oil"])
        - processes: list of cooking/preservation methods (e.g., ["deep-fried", "battered"])
        - allergens: list of potential allergens (e.g., ["shellfish", "gluten"])
        - categories: list of FDA food categories (e.g., ["seafood", "processed food"])
        
        Example for '새우튀김' (shrimp tempura):
        {{"ingredients": ["shrimp", "wheat flour", "oil"], "processes": ["deep-fried", "battered"], "allergens": ["shellfish", "gluten"], "categories": ["seafood", "processed food"]}}
        
        Return ONLY the JSON object, no additional text.
        """
        
        try:
            response = Settings.llm.complete(decomposition_prompt)
            decomposition = json.loads(response.text.strip())
            
            # 캐싱
            self.decomposition_cache[product_name] = decomposition
            return decomposition
        except:
            # 파싱 실패시 기본값
            return {
                "ingredients": [product_name],
                "processes": [],
                "allergens": [],
                "categories": []
            }

    def _is_compound_food(self, query: str) -> bool:
        """복합 식품 여부 판단"""
        # 한국 음식 패턴
        korean_foods = ["김치", "김밥", "만두", "새우튀김", "불고기", "떡볶이", "비빔밥"]
        # 복합 식품 키워드
        compound_keywords = ["튀김", "볶음", "찜", "구이", "조림"]
        
        query_lower = query.lower()
        return any(food in query for food in korean_foods) or \
               any(keyword in query for keyword in compound_keywords)

    def _extract_product_name(self, query: str) -> str:
        """쿼리에서 제품명 추출"""
        # 간단한 패턴 매칭
        korean_foods = ["김치", "김밥", "만두", "새우튀김", "불고기", "떡볶이", "비빔밥"]
        for food in korean_foods:
            if food in query:
                return food
        
        # 패턴으로 추출 시도
        patterns = [
            r"'([^']+)'",  # '제품명' 형태
            r"\"([^\"]+)\"",  # "제품명" 형태
            r"([가-힣]+(?:튀김|볶음|찜|구이))",  # 한글+조리법
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query)
            if match:
                return match.group(1)
        
        return query.split()[0]  # 첫 단어 반환

    def _augment_query(self, original_query: str, decomposition: dict) -> str:
        """분해된 정보로 쿼리 증강"""
        augmented = f"""
User Question: {original_query}

IMPORTANT - Search systematically for these components:
1. Main ingredients: {', '.join(decomposition.get('ingredients', []))}
2. Processing methods: {', '.join(decomposition.get('processes', []))}  
3. Allergens to check: {', '.join(decomposition.get('allergens', []))}
4. FDA categories: {', '.join(decomposition.get('categories', []))}

Search strategy:
- First, try general seafood or main category regulations
- Then check specific processing requirements
- Finally verify allergen labeling requirements
- Stop searching if you find relevant comprehensive information
"""
        return augmented

    def _extract_citations_from_response(self, response) -> dict:
        """Extract citations (title/url) from LlamaIndex response source nodes."""
        citations = []
        sources = []
        keywords = []
        try:
            if hasattr(response, 'source_nodes') and response.source_nodes:
                for node in response.source_nodes:
                    meta = getattr(node, 'metadata', {}) or {}
                    title = meta.get('title') or meta.get('document_title') or meta.get('collection') or 'Reference'
                    url = meta.get('url') or meta.get('source') or meta.get('link')
                    description = meta.get('summary') or meta.get('description') or '관련 규정/자료'
                    if url:
                        item = {"title": title, "description": description, "url": url}
                        if item not in citations:
                            citations.append(item)
                            sources.append(title)
                    # derive simple keywords from tool/collection
                    tool_name = meta.get('tool_name') or meta.get('collection')
                    if tool_name:
                        keywords.append(tool_name)
        except Exception:
            pass
        return {"cfr_references": citations, "sources": sources, "keywords": list(dict.fromkeys(keywords))}

    def chat(self, query: str) -> dict:
        """LLM 분해를 포함한 향상된 채팅 메서드"""
        try:
            # [수정] LLM 필터를 사용하여 질문 의도 파악
            if self._is_food_export_question_llm(query):
                product = self._extract_product_name(query)
                decomposition = self._decompose_product(product)
                
                # 쿼리 증강
                enhanced_query = self._augment_query(query, decomposition)
                
                # 컨텍스트 추가
                context = self.memory.get_context_for_agent()
                full_query = f"{context}\n{enhanced_query}" if context else enhanced_query
            else:
                # 일반 쿼리 처리
                context = self.memory.get_context_for_agent()
                full_query = f"{context}\n{query}" if context else query
            
            # ReAct 에이전트 실행
            response = self.agent.chat(full_query)
            response_text = str(response)
            citations = self._extract_citations_from_response(response)
            
            # 메모리 저장
            used_tools = self._extract_used_tools(response)
            self.memory.add_message("user", query)
            self.memory.add_message("assistant", response_text, used_tools)
            
            return {
                "content": response_text,
                "cfr_references": citations.get("cfr_references", []),
                "sources": citations.get("sources", []),
                "keywords": citations.get("keywords", []),
            }
            
        except ValueError as e:
            if "max iterations" in str(e).lower():
                # Max iterations 에러 처리
                fallback_response = self._generate_fallback_response(query)
                self.memory.add_message("user", query)
                self.memory.add_message("assistant", fallback_response, ["fallback"])
                return {"content": fallback_response, "cfr_references": [], "sources": [], "keywords": []}
            raise e

    def _generate_fallback_response(self, query: str) -> str:
        """검색 실패시 폴백 응답"""
        return f"""
죄송합니다. '{query}'에 대한 구체적인 정보를 데이터베이스에서 찾을 수 없습니다.

일반적으로 식품 수출 시 확인해야 할 FDA 규제 사항:

1. **제조 시설 요구사항**
   - FDA 시설 등록 (Food Facility Registration)
   - HACCP 또는 HARPC 계획 수립

2. **라벨링 규정**
   - 영양성분표 (Nutrition Facts)
   - 원재료 목록 (Ingredient List)
   - 알레르기 유발 물질 표시

3. **식품 안전 기준**
   - 미생물 한계 기준 준수
   - 잔류 농약 및 중금속 기준

더 구체적인 정보가 필요하시면 FDA 공식 웹사이트나 전문 컨설턴트 상담을 권장합니다.
"""
    
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
