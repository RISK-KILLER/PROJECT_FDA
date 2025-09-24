# utils/agent.py
"""
ReAct 프레임워크를 사용하여 FDA 규제 질문에 답변하는 메인 에이전트.
"""
import os
import json
import re
from typing import List, Dict
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.embeddings.openai import OpenAIEmbedding

from utils.tools import create_fda_tools
from utils.memory import ConversationMemory, ChatMessage
from utils.collection_strategy import COLLECTION_STRATEGY

class FDAAgent:
    def __init__(self):
        # LlamaIndex 전역 설정 (rag_engine과 동일하게 설정)
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", api_key=os.getenv("OPENAI_API_KEY"))
        Settings.llm = OpenAI(model="gpt-4-turbo", temperature=0.1, api_key=os.getenv("OPENAI_API_KEY"))

        # 1. 모든 FDA 컬렉션을 '전문가 툴'로 변환
        self.fda_tools = create_fda_tools()

        # 멀티턴 대화를 위한 메모리 추가
        self.memory = ConversationMemory()
        
        # 제품 분해 캐시 추가
        self.decomposition_cache = {}

        # ✅ [수정] 에이전트의 행동 방식을 정의하는 새로운 시스템 프롬프트 (Golden Rule 포함)
        system_prompt = """## 최상위 규칙 (Golden Rule)
- **절대 사전 지식만으로 답변하지 마세요.** 반드시 도구를 사용하여 검색하세요.
- **이전 대화 컨텍스트를 활용하세요.**

당신은 FDA 규제 전문가입니다. 다음 7개 전문 도구를 활용하세요:

1. **usc**: 법적 기반 확인 (21 USC)
2. **ecfr**: 구체적 규정 확인 (21 CFR)  
3. **guidance**: 실무 가이드 (CPG, 라벨링, 알레르기)
4. **gras**: 재료 안전성 확인
5. **dwpe**: Import Alert 확인
6. **fsvp**: 수입자 검증 의무
7. **rpm**: 수입 운영 절차

## 검색 전략
1. 먼저 **guidance**로 실무 가이드 확인
2. **ecfr**로 구체적 규정 확인
3. **gras**로 각 재료 안전성 검증
4. **dwpe**로 수입 거부 이력 확인
5. 필요시 **fsvp**, **rpm**, **usc** 추가 검색

각 도구는 특화된 정보를 제공하므로, 질문에 맞는 도구를 선택하세요.
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
        """제품 분해 (10개 요소) - 한국 음식 지원 강화"""
        # 캐시 확인
        if product_name in self.decomposition_cache:
            return self.decomposition_cache[product_name]
        
        # 한국어 감지 및 처리 지침 추가
        is_korean = any(ord(char) >= 0xAC00 and ord(char) <= 0xD7A3 for char in product_name)
        
        if is_korean:
            prompt_prefix = f"""
You are analyzing a KOREAN food product. First, identify what '{product_name}' is in English.
Common Korean foods:
- 떡볶이 = Tteokbokki (spicy rice cakes)
- 김치 = Kimchi (fermented cabbage)
- 김밥 = Kimbap (rice rolls with vegetables)
- 만두 = Mandu (dumplings)
- 불고기 = Bulgogi (marinated beef)
- 비빔밥 = Bibimbap (mixed rice bowl)
- If not listed above, translate and identify the components.

Now analyze '{product_name}' for FDA requirements.
"""
        else:
            prompt_prefix = f"Analyze '{product_name}' for FDA requirements."
        
        decomposition_prompt = f"""{prompt_prefix}
        
Return a JSON object with EXACTLY these fields:
{{
  "ingredients": [list of main components in English],
  "processes": [manufacturing/cooking methods],
  "allergens": [only FDA major allergens if present: milk, eggs, fish, shellfish, tree nuts, peanuts, wheat, soybeans, sesame],
  "origin": "Korea" if Korean food else appropriate country,
  "category": "ethnic food" if Korean else appropriate category,
  "subcategories": [relevant subcategories],
  "storage_type": "frozen", "refrigerated", or "ambient",
  "risk_level": "high", "medium", or "low",
  "packaging_concerns": [relevant concerns],
  "potential_hazards": [food safety hazards],
  "import_type": "commercial" or "personal use"
}}

Examples:
- For 떡볶이: {{"ingredients": ["rice cake", "fish cake", "gochujang"], ...}}
- For 김치: {{"ingredients": ["cabbage", "chili powder", "garlic"], ...}}

Return ONLY valid JSON, no other text or markdown.
"""
        
        try:
            response = Settings.llm.complete(decomposition_prompt)
            text = response.text.strip()
            
            # Markdown 코드 블록 제거
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()
            
            # JSON 파싱
            decomposition = json.loads(text)
            
            # 필드 검증 및 기본값 추가
            defaults = {
                "ingredients": [],
                "processes": [],
                "allergens": [],
                "origin": "Korea" if is_korean else "unknown",
                "category": "ethnic food" if is_korean else "food",
                "subcategories": [],
                "storage_type": "ambient",
                "risk_level": "medium",
                "packaging_concerns": [],
                "potential_hazards": [],
                "import_type": "commercial"
            }
            
            # 누락된 필드 채우기
            for key, default_value in defaults.items():
                if key not in decomposition or not decomposition[key]:
                    decomposition[key] = default_value
            
            # 캐싱
            self.decomposition_cache[product_name] = decomposition
            return decomposition
            
        except (json.JSONDecodeError, Exception) as e:
            print(f"Decomposition failed for '{product_name}': {e}")
            print(f"LLM Response: {response.text if 'response' in locals() else 'No response'}")
            
            # 스마트한 폴백: LLM 한 번 더 시도 (더 간단한 방식)
            try:
                simple_prompt = f"""
What are the main ingredients of {product_name}?
Answer in this exact format:
ingredients: item1, item2, item3
allergens: allergen1, allergen2
"""
                simple_response = Settings.llm.complete(simple_prompt)
                lines = simple_response.text.strip().split('\n')
                
                ingredients = []
                allergens = []
                
                for line in lines:
                    if line.startswith('ingredients:'):
                        ingredients = [i.strip() for i in line.split(':')[1].split(',')]
                    elif line.startswith('allergens:'):
                        allergens = [a.strip() for a in line.split(':')[1].split(',')]
                
                return {
                    "ingredients": ingredients or [product_name],
                    "processes": ["processing", "packaging"],
                    "allergens": allergens,
                    "origin": "Korea" if is_korean else "unknown",
                    "category": "ethnic food" if is_korean else "food",
                    "subcategories": ["imported food"],
                    "storage_type": "refrigerated" if is_korean else "ambient",
                    "risk_level": "medium",
                    "packaging_concerns": ["labeling required"],
                    "potential_hazards": ["contamination"],
                    "import_type": "commercial"
                }
                
            except:
                # 최종 폴백
                return {
                    "ingredients": [product_name],
                    "processes": [],
                    "allergens": [],
                    "origin": "Korea" if is_korean else "unknown",
                    "category": "ethnic food" if is_korean else "food",
                    "subcategories": [],
                    "storage_type": "ambient",
                    "risk_level": "medium",
                    "packaging_concerns": [],
                    "potential_hazards": [],
                    "import_type": "commercial"
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
        """분해된 10개 요소를 모두 활용하는 쿼리 증강"""
        augmented = f"""
User Question: {original_query}

PRODUCT ANALYSIS (10 elements):
1. Ingredients: {', '.join(decomposition.get('ingredients', []))}
2. Processes: {', '.join(decomposition.get('processes', []))}  
3. Allergens: {', '.join(decomposition.get('allergens', []))}
4. Origin: {decomposition.get('origin', 'unknown')}
5. Category: {decomposition.get('category', 'food')}
6. Subcategories: {', '.join(decomposition.get('subcategories', []))}
7. Storage: {decomposition.get('storage_type', 'ambient')}
8. Risk Level: {decomposition.get('risk_level', 'medium')}
9. Packaging Concerns: {', '.join(decomposition.get('packaging_concerns', []))}
10. Potential Hazards: {', '.join(decomposition.get('potential_hazards', []))}

SEARCH STRATEGY (7 collections):
1. guidance: 실무 가이드 (CPG, 라벨링, 알레르기)
2. ecfr: 구체적 규정 (21 CFR)
3. gras: 재료 안전성 확인
4. dwpe: Import Alert 확인
5. fsvp: 수입자 검증 의무
6. rpm: 수입 운영 절차
7. usc: 법적 기반 (21 USC)

Use the most relevant collections based on the product characteristics above.
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

    def _format_parallel_results(self, results: List[Dict]) -> str:
        """병렬 검색 결과를 텍스트로 포맷 (가중치 없음)"""
        if not results:
            return "병렬 검색 결과 없음"
        
        formatted = []
        for i, result in enumerate(results[:5], 1):
            formatted.append(f"""
{i}. [{result['score']:.2f}] {result['collection']} {result.get('collection_role', '')}
   제목: {result.get('title', 'N/A')}
   내용: {result.get('text', 'N/A')}...
   출처: {result.get('collection_desc', '')}
""")
        
        return "\n".join(formatted)

    def chat(self, query: str) -> dict:
        """Phase 1: 병렬 검색 + ReAct 분석"""
        try:
            # 1. 질문 분류 및 분해
            if self._is_food_export_question_llm(query):
                product = self._extract_product_name(query)
                decomposition = self._decompose_product(product)
                
                # 2. Phase 1 핵심: 병렬 검색 먼저 실행
                print("🔍 병렬 검색 시작...")
                from utils.orchestrator import SimpleOrchestrator
                orchestrator = SimpleOrchestrator()
                
                # 관련 컬렉션 결정
                collections = orchestrator.determine_collections(decomposition)
                print(f"📚 검색할 컬렉션: {collections}")
                
                try:
                    # 병렬 검색 실행
                    parallel_results = orchestrator.parallel_search(
                        query="ethnic food import export",  # 기본 FDA 용어
                        collections=collections,
                        decomposition=decomposition  # 분해 정보 전달
                    )
                    
                    # 결과 병합 및 순위화 (순수 점수 기반)
                    ranked_results = orchestrator.merge_and_rank(parallel_results)
                    print(f"⚡ 병렬 검색 완료: {parallel_results['search_time']:.2f}초, {len(ranked_results)}개 결과")
                    
                    # 3. 병렬 검색 결과를 컨텍스트에 포함
                    search_summary = self._format_parallel_results(ranked_results)
                    
                    enhanced_query = f"""
{self._augment_query(query, decomposition)}

=== 병렬 검색 결과 (이미 수집됨) ===
{search_summary}

위 병렬 검색 결과를 참고하되, 부족한 부분은 추가 도구를 사용하여 보완하세요.
주의: 이미 찾은 정보는 다시 검색하지 마세요.
"""
                except Exception as e:
                    print(f"병렬 검색 실패: {e}, 기존 방식으로 진행")
                    enhanced_query = self._augment_query(query, decomposition)
                
                # 4. ReAct Agent가 병렬 검색 결과를 기반으로 심화 분석
                context = self.memory.get_context_for_agent()
                full_query = f"{context}\n{enhanced_query}" if context else enhanced_query
                
            else:
                # 일반 쿼리는 기존 방식
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
            
        except Exception as e:
            print(f"Error in chat: {e}")
            fallback = self._generate_fallback_response(query)
            return {
                "content": fallback,
                "cfr_references": [],
                "sources": [],
                "keywords": []
            }

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
