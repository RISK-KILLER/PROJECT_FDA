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

        # ✅ [수정] 에이전트의 행동 방식을 정의하는 새로운 시스템 프롬프트 (정보 수집 전용)
        system_prompt = """당신은 FDA 규제 정보 수집 전문가입니다.

## 역할
사용자 질문에 답하기 위해 필요한 정보를 도구로 수집하세요.
최종 답변은 생성하지 마세요. 정보만 수집하세요.

## 수집해야 할 정보
1. CFR 규정 (구체적 번호 + 내용)
2. Import Alert 확인
3. 라벨링 요구사항
4. FSVP/검증 절차
5. 기타 관련 규제 정보

## 출력 형식
수집한 정보를 구조화된 형식으로 정리하세요:

**CFR 규정:**
- [규정 번호]: [내용]

**Import Alert:**
- [Alert 번호]: [내용]

**라벨링:**
- [요구사항]

**FSVP:**
- [절차]

## 중요
- 제공된 검색 결과를 우선 참고하세요
- 부족한 정보만 도구로 추가 검색하세요
- 한국어 쿼리는 반드시 영어로 변환하세요

## 도구 사용 강제 케이스
다음 키워드 포함 시 무조건 도구 사용:
- "비용", "cost", "payment", "supervision", "누가"
- "절차", "procedure", "process", "어떻게"
- "Chapter", "Section", "GRN", "CFR", "USC"
- "규정", "regulation", "requirement"
- "relabeling", "detention", "import", "GRAS"

**도구 회피 금지:**
❌ "(Implicit) I can answer without tools" → 절대 금지
❌ "일반적으로 알려진 바로는..." → 금지
✅ 반드시: Action → Observation → Answer 순서

## 최상위 규칙 (Golden Rule)
- 절대 사전 지식만으로 답변하지 마세요. 반드시 도구를 사용하여 검색하세요.
- **한국어 쿼리는 반드시 영어로 변환하여 도구에 전달하세요.**
- **도구를 선택하기 전에 쿼리를 분석하세요.**

## 쿼리 분석 절차 (도구 선택 전 필수!)

**Step 1: 쿼리 언어 확인**
- 한국어 있음 → 영어로 변환 필요
- 영어만 있음 → 그대로 사용

**Step 2: 키워드 기반 도구 판별**
- "GRN", "GRAS", "물질", "첨가물" → **gras/gras_approved/gras_withdrawn**
- "CFR", "21 CFR", "규정" → **ecfr**
- "Import Alert", "Red List", "수입 거부" → **dwpe**
- "Chapter", "Section", "RPM", "절차", "procedure" → **rpm**
- "21 USC", "법률", "처벌" → **usc**
- "FSVP", "수입자", "검증" → **fsvp**
- "Guidance", "라벨링" → **guidance**

## 검색 쿼리 작성 (영어 변환 필수!)

### RPM 한영 변환
- "개인용 수입" → "personal use importation"
- "절차" → "procedures process"
- "검사 거부" → "refusal entry detention"
- "relabeling 비용" → "relabeling supervision costs payment"
- "누가 내?" → "who pays costs responsibility"

### GRAS 한영 변환
- "대두" → "soy soybean"
- "음료" → "beverage drink water"

### eCFR 한영 변환
- "냉동식품" → "frozen food"
- "HACCP" → "HACCP hazard analysis"

### DWPE 한영 변환 + 동의어
- "해산물" → "fish fishery seafood shellfish aquatic marine"
- "중국" → "China Chinese"

### USC 한영 변환
- "부정표시" → "misbranding false labeling"
- "처벌" → "penalties violations"

## 재시도 전략
첫 검색 실패 시 2-3번 재시도 필수
"""

        # 2. ReAct 에이전트 생성 (context 추가)
        self.agent = ReActAgent.from_tools(
            tools=self.fda_tools,
            llm=Settings.llm,
            system_prompt=system_prompt,
            max_iterations=10,
            verbose=True,
            # ✅ 핵심 추가: context로 도구 강제 사용
            context="""You MUST use tools for FDA-related queries.
NEVER answer with "(Implicit) I can answer without tools".
For keywords like "비용/cost", "절차/procedure", "Chapter", "relabeling" → ALWAYS use tools.
Always translate Korean to English before searching."""
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

    def _extract_product_name(self, query: str) -> str:
        """LLM을 사용하여 쿼리에서 제품명 추출"""
        prompt = f"""
Analyze this user query and determine if it contains a FOOD PRODUCT name.

Query: "{query}"

Rules:
- Return ONLY the food product name if one exists
- Return "None" if this is a general question (about regulations, procedures, concepts)
- Examples of products: "김치", "새우튀김", "냉동만두", "chicken nuggets"
- Examples of NOT products: "HACCP", "FDA", "규정", "절차", "라벨링"

Answer with ONLY the product name or "None":
"""
        
        try:
            response = Settings.llm.complete(prompt)
            result = response.text.strip()
            
            # "None" 또는 "none" 반환 시 None으로 변환
            if result.lower() == "none":
                return None
            
            return result
            
        except Exception as e:
            print(f"LLM product extraction failed: {e}")
            # 에러 시 안전하게 None 반환
            return None

    def _augment_general_query(self, original_query: str) -> str:
        """일반 질문에 대한 LLM 쿼리 증강"""
        prompt = f"""
다음 사용자 질문을 FDA 규제 데이터베이스 검색에 최적화된 영어 쿼리로 변환하고 확장하세요.

사용자 질문: {original_query}

다음 요소들을 포함하여 검색 쿼리를 생성하세요:
1. 핵심 키워드를 영어로 변환
2. 관련 동의어 및 전문 용어 추가
3. FDA 규제 맥락에 맞는 검색어 확장
4. 컬렉션별 특화 키워드 포함

예시:
- "비용이 얼마나 드나요?" → "costs payment fees supervision relabeling expenses"
- "어떤 절차가 필요한가요?" → "procedures process requirements steps documentation"
- "규정은 무엇인가요?" → "regulations requirements CFR guidelines compliance"

변환된 검색 쿼리만 반환하세요 (설명 없이):
"""
        
        try:
            response = Settings.llm.complete(prompt)
            augmented_query = response.text.strip()
            
            # 원본 쿼리와 증강된 쿼리 결합
            return f"{original_query}\n\nEnhanced search query: {augmented_query}"
            
        except Exception as e:
            print(f"Query augmentation failed: {e}")
            return original_query

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
        """병렬 검색 결과를 텍스트로 포맷"""
        if not results:
            return "병렬 검색 결과 없음"
        
        formatted = []
        for i, result in enumerate(results[:10], 1):  # 5 → 10개로 증가
            formatted.append(f"""
{i}. [{result['score']:.2f}] {result['collection']} {result.get('collection_role', '')}
   제목: {result.get('title', 'N/A')}
   내용: {result.get('text', 'N/A')[:800]}...  # 200 → 800자로 증가
   출처: {result.get('collection_desc', '')}
""")
        
        return "\n".join(formatted)

    def chat(self, query: str) -> dict:
        """사용자 제안 구조: 제품 질문은 분해, 일반 질문은 LLM 증강"""
        try:
            product = self._extract_product_name(query)
            
            if product:
                # 제품 질문: 분해 방식
                print(f"📦 제품 질문 감지: {product}")
                decomposition = self._decompose_product(product)
                search_query = query  # 원본 사용
                print(f"🔬 제품 분해 완료: {decomposition.get('category')}")
            else:
                # 일반 질문: LLM 증강 방식
                print("🔍 일반 질문 감지 - LLM 증강 적용")
                decomposition = None
                search_query = self._augment_general_query(query)  # 여기서 증강!
                print(f"✨ 증강된 쿼리: {search_query[:100]}...")
            
            # orchestrator에 전달 (순수 검색만 담당)
            from utils.orchestrator import SimpleOrchestrator
            orchestrator = SimpleOrchestrator()
            
            if decomposition:
                # 제품 질문: 분해 기반 컬렉션 선택
                collections = orchestrator.determine_collections(decomposition)
            else:
                # 일반 질문: 기본 컬렉션 사용
                collections = ['guidance', 'ecfr', 'gras', 'dwpe', 'fsvp', 'rpm', 'usc']
            
            print(f"📚 검색할 컬렉션: {collections}")
            
            # 병렬 검색 실행
            parallel_results = orchestrator.parallel_search(
                query=search_query,  # 증강된 또는 원본
                collections=collections,
                decomposition=decomposition
            )
            
            ranked_results = orchestrator.merge_and_rank(parallel_results)
            print(f"⚡ 병렬 검색 완료: {parallel_results['search_time']:.2f}초, {len(ranked_results)}개 결과")
            
            # 결과 충분성 평가 및 응답 생성
            if self._is_parallel_result_sufficient(ranked_results, decomposition or {}):
                # decomposition 있든 없든, 충분하면 직접 답변
                print("✅ 병렬 검색 결과만으로 충분 - 직접 답변 생성")
                return self._generate_direct_response(query, ranked_results, decomposition)
            else:
                # ReAct Agent로 추가 정보 수집
                print("🔄 ReAct Agent로 추가 정보 수집")
                search_summary = self._format_parallel_results(ranked_results)
                
                if decomposition:
                    enhanced_query = f"""
{self._augment_query(query, decomposition)}

## 검색된 FDA 문서들
{search_summary}

위 정보를 활용하고, 부족한 부분만 추가 검색하세요.
정보 수집만 하고, 최종 답변은 생성하지 마세요.
"""
                else:
                    enhanced_query = f"""
{search_query}

## 검색된 FDA 문서들
{search_summary}

위 정보를 활용하고, 부족한 부분만 추가 검색하세요.
정보 수집만 하고, 최종 답변은 생성하지 마세요.
"""
                
                context = self.memory.get_context_for_agent()
                full_query = f"{context}\n{enhanced_query}" if context else enhanced_query
                
                # Agent로 정보 수집만
                print("🔍 Agent 정보 수집 시작...")
                agent_response = self.agent.chat(full_query)
                collected_info = str(agent_response)
                
                # 병렬 검색 + Agent 정보를 합쳐서 최종 답변 생성
                print("✅ 정보 수집 완료 - 최종 답변 생성")
                return self._generate_response_with_agent_info(
                    query=query,
                    parallel_results=ranked_results,
                    agent_info=collected_info,
                    decomposition=decomposition
                )
            
        except Exception as e:
            print(f"Error in chat: {e}")
            fallback = self._generate_fallback_response(query)
            return {
                "content": fallback,
                "cfr_references": [],
                "sources": [],
                "keywords": []
            }

    def _is_parallel_result_sufficient(self, results: List[Dict], decomposition: dict) -> bool:
        """병렬 검색 결과의 충분성 평가 (제품 질문과 일반 질문 모두 지원)"""
        print(f"\n🔍 충분성 평가 시작")
        print(f"  - 전체 결과 개수: {len(results)}")
        
        # 기본 조건 체크
        if not results or len(results) < 5:
            print(f"  ❌ 결과 부족: {len(results)}개")
            return False
        
        # GRAS 필터링 - 일단 비활성화
        # filtered_results = self._filter_gras_noise(results, decomposition)
        filtered_results = results  # 그대로 사용
        
        # 평균 점수 계산
        avg_score = sum(r['score'] for r in filtered_results) / len(filtered_results)
        print(f"  - 평균 점수: {avg_score:.3f} (임계값: 0.60)")
        if avg_score < 0.60:
            print(f"  ❌ 평균 점수 부족")
            return False
        
        # 컬렉션 다양성 체크 (최소 3개 이상의 컬렉션에서 결과)
        unique_collections = set(r['collection'] for r in filtered_results)
        print(f"  - 컬렉션 다양성: {len(unique_collections)}개 {list(unique_collections)}")
        if len(unique_collections) < 3:
            print(f"  ❌ 컬렉션 다양성 부족")
            return False
        
        # 핵심 컬렉션 포함 여부 체크 (일반 질문도 동일한 기준 적용)
        essential_collections = {'guidance', 'ecfr', 'gras'}  # 라벨링, 규정, 안전성
        has_essential = [c for c in essential_collections if c in unique_collections]
        print(f"  - 필수 컬렉션: {has_essential}")
        if not has_essential:
            print(f"  ❌ 필수 컬렉션 없음")
            return False
        
        # 알레르기 정보가 필요한 경우 guidance 결과 필수 (제품 질문만)
        # if decomposition and decomposition.get('allergens') and 'guidance' not in unique_collections:
        #     return False
        
        print(f"  ✅ 충분성 평가 통과!\n")
        return True

    def _generate_direct_response(self, query: str, results: List[Dict], decomposition: dict) -> dict:
        """병렬 검색 결과만으로 직접 답변 생성 (제품 질문과 일반 질문 모두 지원)"""
        
        # 출처 번호 매핑 생성
        citations = []
        for i, r in enumerate(results[:10], 1):
            # 제목이 비어있거나 None인 경우 기본값 설정
            title = r.get('title', '').strip()
            if not title:
                title = f"{r['collection'].upper()} Document {i}"
            
            # URL이 비어있는 경우 기본 URL 생성
            url = r.get('url', '').strip()
            if not url:
                # 컬렉션별 기본 URL 생성
                if r['collection'] == 'fsvp':
                    url = f"https://www.fda.gov/food/importing-food-products-united-states/foreign-suppliers-verification-programs-fsvp-importer-portal-records-submission"
                elif r['collection'] == 'gras':
                    url = f"https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=GRASNotices"
                elif r['collection'] == 'ecfr':
                    url = f"https://www.ecfr.gov/current/title-21"
                elif r['collection'] == 'guidance':
                    url = f"https://www.fda.gov/regulatory-information/search-fda-guidance-documents"
                elif r['collection'] == 'dwpe':
                    url = f"https://www.accessdata.fda.gov/cms_ia/country_KR.html"
                elif r['collection'] == 'usc':
                    url = f"https://www.law.cornell.edu/uscode/text/21"
            
            citations.append({
                "index": i,
                "collection": r['collection'],
                "title": title,
                "url": url,
                "score": r['score']
            })
        
        # 출처 리스트 (프롬프트용)
        source_list = "\n".join([
            f"[출처 {c['index']}] {c['collection']}: {c['title'][:80]}"
            for c in citations
        ])
        
        # 전체 검색 결과를 풍부하게 전달
        full_context = "\n\n".join([
            f"[출처 {i+1}] {r['collection'].upper()} (점수: {r['score']:.3f})\n"
            f"제목: {r.get('title', 'N/A')}\n"
            f"내용: {r.get('text', '')[:800]}"
            for i, r in enumerate(results[:10])
        ])
        
        if decomposition:
            prompt = f"""
사용자 질문: {query}

제품 특성:
{json.dumps(decomposition, indent=2, ensure_ascii=False)}

📖 문서 컨텍스트 (각 내용 앞의 [출처 N]을 보고 주석을 달아야 함):
{full_context}

## 출처 목록
{source_list}

위 문서들을 종합하여 다음 사항을 포함한 답변을 작성하세요:
1. 구체적인 CFR 규정 번호와 내용
2. Import Alert 여부
3. 알레르기 라벨링 구체적 요구사항
4. FSVP 검증 절차
5. 실무 체크리스트

❗️핵심 규칙:
- 중요한 정보나 규정을 언급할 때마다 해당하는 출처 번호를 [1], [2] 형태로 문장 끝에 삽입하세요.
- 여러 출처를 참고한 경우 [1][2] 처럼 연속으로 표시하세요.
- 반드시 [출처 N] 정보를 확인하고 정확한 번호를 사용하세요.

예시:
- 새우는 주요 알레르기 유발 물질로 표시해야 합니다[1].
- 21 CFR 1250.26과 Import Alert 16-50을 준수해야 합니다[2][3].

한국어로 구체적이고 실용적인 답변을 제공하세요.
"""
        else:
            prompt = f"""
사용자 질문: {query}

📖 문서 컨텍스트 (각 내용 앞의 [출처 N]을 보고 주석을 달아야 함):
{full_context}

## 출처 목록
{source_list}

위 문서들을 종합하여 답변하되, **각 주장 뒤에 [1], [2] 형식으로 출처 번호를 표시**하세요.

❗️핵심 규칙:
- 중요한 정보나 규정을 언급할 때마다 해당하는 출처 번호를 [1], [2] 형태로 문장 끝에 삽입하세요.
- 여러 출처를 참고한 경우 [1][2] 처럼 연속으로 표시하세요.

예시:
- FDA는 식품 알레르기 표시를 의무화하고 있습니다[1].
- 21 CFR 규정을 준수해야 합니다[2][3].

한국어로 명확하고 실용적인 답변을 제공하세요.
"""
        
        response = Settings.llm.complete(prompt)
        
        print(f"\n📋 Citations 생성 완료:")
        print(f"  - 총 {len(citations)}개 citations 생성")
        for c in citations:
            print(f"    [{c['index']}] {c['collection']}: {c['title'][:50]}...")
        
        return {
            "content": response.text,
            "citations": citations,
            "cfr_references": [],
            "sources": [c['title'] for c in citations[:5]],
            "keywords": list(set(r['collection'] for r in results))
        }

    def _generate_response_with_agent_info(
        self, 
        query: str, 
        parallel_results: List[Dict],
        agent_info: str,
        decomposition: dict
    ) -> dict:
        """병렬 검색 + Agent 수집 정보를 종합하여 답변 생성"""
        
        print("\n" + "="*60)
        print("📝 최종 답변 생성 시작")
        print("="*60)
        
        # 출처 번호 매핑 생성
        citations = []
        for i, r in enumerate(parallel_results[:10], 1):
            # 제목이 비어있거나 None인 경우 기본값 설정
            title = r.get('title', '').strip()
            if not title:
                title = f"{r['collection'].upper()} Document {i}"
            
            # URL이 비어있는 경우 기본 URL 생성
            url = r.get('url', '').strip()
            if not url:
                # 컬렉션별 기본 URL 생성
                if r['collection'] == 'fsvp':
                    url = f"https://www.fda.gov/food/importing-food-products-united-states/foreign-suppliers-verification-programs-fsvp-importer-portal-records-submission"
                elif r['collection'] == 'gras':
                    url = f"https://www.hfpappexternal.fda.gov/scripts/fdcc/index.cfm?set=GRASNotices"
                elif r['collection'] == 'ecfr':
                    url = f"https://www.ecfr.gov/current/title-21"
                elif r['collection'] == 'guidance':
                    url = f"https://www.fda.gov/regulatory-information/search-fda-guidance-documents"
                elif r['collection'] == 'dwpe':
                    url = f"https://www.fda.gov/import-alerts"
                elif r['collection'] == 'usc':
                    url = f"https://www.law.cornell.edu/uscode/text/21"
            
            citations.append({
                "index": i,
                "collection": r['collection'],
                "title": title,
                "url": url,
                "score": r['score']
            })
        
        # 출처 리스트 (프롬프트용)
        source_list = "\n".join([
            f"[출처 {c['index']}] {c['collection']}: {c['title'][:80]}"
            for c in citations
        ])
        
        # 병렬 검색 결과 정리 (Streamlit 스타일)
        parallel_context = "\n\n".join([
            f"[출처 {i+1}] {r['collection'].upper()} (점수: {r['score']:.3f})\n"
            f"제목: {r.get('title', 'N/A')}\n"
            f"내용: {r.get('text', '')[:800]}"
            for i, r in enumerate(parallel_results[:10])
        ])
        
        print(f"📊 입력 정보:")
        print(f"  - 병렬 검색 결과: {len(parallel_results)}개")
        print(f"  - Agent 수집 정보: {len(agent_info)}자")
        print(f"  - 총 컨텍스트: {len(parallel_context) + len(agent_info)}자")
        
        # 통합 프롬프트
        if decomposition:
            prompt = f"""
사용자 질문: {query}

제품 특성:
{json.dumps(decomposition, indent=2, ensure_ascii=False)}

📖 문서 컨텍스트 (각 내용 앞의 [출처 N]을 보고 주석을 달아야 함):
{parallel_context}

Agent가 추가 수집한 정보:
{agent_info}

## 출처 목록
{source_list}

위 모든 정보를 종합하여 다음을 포함한 답변을 작성하세요:
1. 구체적인 CFR 규정 번호와 내용
2. Import Alert 여부
3. 알레르기 라벨링 구체적 요구사항
4. FSVP 검증 절차
5. 실무 체크리스트 (5개 이상)

❗️핵심 규칙:
- 중요한 정보나 규정을 언급할 때마다 해당하는 출처 번호를 [1], [2] 형태로 문장 끝에 삽입하세요.
- 여러 출처를 참고한 경우 [1][2] 처럼 연속으로 표시하세요.
- 반드시 [출처 N] 정보를 확인하고 정확한 번호를 사용하세요.

예시:
- 새우는 주요 알레르기 유발 물질로 표시해야 합니다[1].
- 21 CFR 1250.26과 Import Alert 16-50을 준수해야 합니다[2][3].

한국어로 500단어 이상, 구체적이고 실용적인 답변을 제공하세요.
"""
        else:
            prompt = f"""
사용자 질문: {query}

📖 문서 컨텍스트 (각 내용 앞의 [출처 N]을 보고 주석을 달아야 함):
{parallel_context}

Agent가 추가 수집한 정보:
{agent_info}

## 출처 목록
{source_list}

위 모든 정보를 종합하여 답변하되, **각 주장 뒤에 [1], [2] 형식으로 출처 번호를 표시**하세요.

❗️핵심 규칙:
- 중요한 정보나 규정을 언급할 때마다 해당하는 출처 번호를 [1], [2] 형태로 문장 끝에 삽입하세요.
- 여러 출처를 참고한 경우 [1][2] 처럼 연속으로 표시하세요.

예시:
- FDA는 식품 알레르기 표시를 의무화하고 있습니다[1].
- 21 CFR 규정을 준수해야 합니다[2][3].

한국어로 명확하고 실용적인 답변을 제공하세요.
"""
        
        print(f"\n🤖 LLM 호출 중... (프롬프트: {len(prompt)}자)")
        
        # 단일 LLM 호출로 최종 답변 생성
        response = Settings.llm.complete(prompt)
        
        print(f"\n✅ 최종 답변 생성 완료!")
        print(f"  - 답변 길이: {len(response.text)}자")
        print(f"  - 답변 단어 수: {len(response.text.split())}단어")
        
        print(f"\n📋 Citations 생성 완료:")
        print(f"  - 총 {len(citations)}개 citations 생성")
        for c in citations:
            print(f"    [{c['index']}] {c['collection']}: {c['title'][:50]}...")
        
        # 최종 답변 내용 출력
        print("\n" + "="*60)
        print("📄 최종 답변 내용:")
        print("="*60)
        print(response.text)
        print("="*60 + "\n")
        
        return {
            "content": response.text,
            "citations": citations,
            "cfr_references": [],
            "sources": [c['title'] for c in citations[:5]],
            "keywords": list(set(r['collection'] for r in parallel_results))
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
