# utils/tools.py
"""
Qdrant 컬렉션을 LlamaIndex의 QueryEngineTool로 변환하는 팩토리 파일.
각 툴은 ReAct 에이전트가 사용할 수 있는 전문가 역할을 합니다.
리랭킹(Reranking) 기능이 각 쿼리 엔진에 적용됩니다.
"""
import os
from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.postprocessor import SentenceTransformerRerank
from qdrant_client import QdrantClient

def create_fda_tools() -> List[QueryEngineTool]:
    """
    모든 FDA 관련 Qdrant 컬렉션을 조회하여 각각을 위한 QueryEngineTool 리스트를 생성합니다.
    """
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"), 
        api_key=os.getenv("QDRANT_API_KEY")
    )

    # [추가] 리랭커 모델 초기화 (cross-encoder)
    # BAAI/bge-reranker-v2-m3 모델은 쿼리-문서 쌍의 관련성을 직접 점수화합니다.
    reranker = SentenceTransformerRerank(
        model="BAAI/bge-reranker-v2-m3",
        top_n=3,
    )

    # Qdrant에 존재하는 모든 컬렉션 이름을 가져옵니다.
    # get_collections()는 CollectionsResponse 객체를 반환하므로, 내부의 .collections 리스트를 사용합니다.
    collections_response = qdrant_client.get_collections()
    collection_names = [col.name for col in collections_response.collections if col.name.startswith(('guidance_', 'regulation_'))]
    
    all_tools = []

    # 각 컬렉션에 대한 상세 설명 (에이전트가 이 설명을 보고 툴을 선택합니다)
    tool_descriptions = {
        "guidance_allergen": "식품의 주요 알레르기 유발 물질(allergen)의 정의, 종류, 그리고 교차 오염 방지 방법에 대한 FDA의 공식 지침(guidance)을 검색합니다.",
        "guidance_labeling": "식품 포장지의 영양 성분표, 원재료 목록, '유기농' 또는 '글루텐 프리'와 같은 특정 문구(claim) 표시 방법에 대한 FDA의 공식 지침(guidance)을 검색합니다.",
        "guidance_additives": "식품 첨가물(additives), 보존료, 색소, 그리고 GRAS(Generally Recognized As Safe) 물질에 대한 FDA의 공식 지침(guidance)을 검색합니다.",
        "guidance_cpg": "FDA의 규정 준수 정책 가이드(Compliance Policy Guides, CPG)를 검색합니다. 특정 식품(예: 수산물, 유제품)에 대한 FDA의 내부 단속 기준, 집행 정책, 위반 사례에 대한 내용을 다룹니다.",
        "regulation_allergen": "식품 알레르기(allergen)와 관련된 미국 연방 규정(CFR) 및 법률(USC)의 원문 조항을 검색합니다.",
        "regulation_labeling": "식품 라벨링(labeling)과 관련된 미국 연방 규정(CFR) 및 법률(USC)의 원문 조항을 검색합니다.",
        "regulation_additives": "식품 첨가물(additives)과 관련된 미국 연방 규정(CFR) 및 법률(USC)의 원문 조항을 검색합니다.",
        "regulation_standards": "특정 식품의 표준 규격, 품질, 정체성(Identity)에 대한 법적 규정을 검색합니다. 특히 '쌀(rice)', '밀가루(flour)' 같은 가공 곡물이나 '치즈', '버터' 같은 유제품의 기준을 확인할 때 유용합니다.",
        "regulation_manufacturing": "식품 제조 시설의 위생, CGMP(Current Good Manufacturing Practice), HACCP 계획에 대한 법적 규정을 검색합니다. 특히 '냉동(frozen)', '저온 살균(pasteurization)', '저온 유통(cold chain)'과 관련된 공정 규정을 찾을 때 사용합니다.",
        "regulation_general": "특정 식품 카테고리에 속하지 않는 일반적인 FDA 법규(regulation)를 검색합니다. 식품 시설 등록, 수입 절차 등 포괄적인 주제를 다룹니다.",
        "regulation_usc": "미국 연방 법전(U.S. Code)의 식품, 의약품, 화장품 관련 최상위 법률 조항 원문을 검색합니다."
    }

    for name in collection_names:
        if name in tool_descriptions:
            # LlamaIndex의 VectorStoreIndex를 사용하여 각 컬렉션에 대한 쿼리 엔진 생성
            vector_store = QdrantVectorStore(client=qdrant_client, collection_name=name)
            index = VectorStoreIndex.from_vector_store(vector_store)
            # 1단계: 벡터 검색으로 상위 후보를 넓게 가져오고, 2단계: 리랭커로 상위 n개를 정밀 선택
            query_engine = index.as_query_engine(
                similarity_top_k=5,
                node_postprocessors=[reranker],
            )

            # QueryEngine을 에이전트가 사용할 수 있는 '툴'로 변환
            tool = QueryEngineTool(
                query_engine=query_engine,
                metadata=ToolMetadata(
                    name=name,
                    description=tool_descriptions[name]
                ),
            )
            all_tools.append(tool)

    return all_tools
