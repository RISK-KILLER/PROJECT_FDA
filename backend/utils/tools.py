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

    # 각 컬렉션에 대한 설명 (에이전트가 이 설명을 보고 툴을 선택합니다)
    tool_descriptions = {
        "guidance_allergen": "식품 알레르기(allergen)에 대한 FDA의 지침(guidance) 문서를 검색합니다.",
        "guidance_labeling": "식품 라벨링(labeling) 및 영양 정보 표시에 대한 FDA의 지침(guidance) 문서를 검색합니다.",
        "guidance_additives": "식품 첨가물(additives) 및 색소에 대한 FDA의 지침(guidance) 문서를 검색합니다.",
        "guidance_cpg": "FDA의 규정 준수 정책 가이드(Compliance Policy Guides, CPG) 문서를 검색합니다. 주로 단속, 집행, 위반 사례에 대한 내용을 다룹니다.",
        "regulation_allergen": "식품 알레르기(allergen)에 대한 CFR, USC 등 법적 규정(regulation)을 검색합니다.",
        "regulation_labeling": "식품 라벨링(labeling)에 대한 CFR, USC 등 법적 규정(regulation)을 검색합니다.",
        "regulation_additives": "식품 첨가물(additives)에 대한 CFR, USC 등 법적 규정(regulation)을 검색합니다.",
        "regulation_standards": "특정 식품(치즈, 빵 등)의 표준, 품질, 정체성에 대한 법적 규정(regulation)을 검색합니다.",
        "regulation_manufacturing": "식품 제조 시설, 위생, CGMP 등 제조 공정에 대한 법적 규정(regulation)을 검색합니다.",
        "regulation_general": "특정 카테고리에 속하지 않는 일반적인 FDA 법규(regulation)를 검색합니다.",
        "regulation_usc": "미국 연방 법전(U.S. Code)의 식품 관련 조항을 검색합니다."
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
