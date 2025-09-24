# utils/tools.py
import os
from typing import List
from llama_index.core import VectorStoreIndex
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from utils.collection_strategy import COLLECTION_STRATEGY

def create_fda_tools() -> List[QueryEngineTool]:
    """실제 7개 FDA Qdrant 컬렉션을 QueryEngineTool로 변환"""
    qdrant_client = QdrantClient(
        url=os.getenv("QDRANT_URL"), 
        api_key=os.getenv("QDRANT_API_KEY")
    )

    actual_collections = ['dwpe', 'ecfr', 'fsvp', 'gras', 'guidance', 'rpm', 'usc']
    
    all_tools = []

    for name in actual_collections:
        if name in COLLECTION_STRATEGY:
            strategy = COLLECTION_STRATEGY[name]
            
            try:
                # 표준 벡터 스토어 사용 (커스터마이징 불필요!)
                vector_store = QdrantVectorStore(
                    client=qdrant_client,
                    collection_name=name
                )
                
                # 인덱스 생성
                index = VectorStoreIndex.from_vector_store(vector_store)
                
                # 쿼리 엔진 생성
                query_engine = index.as_query_engine(
                    similarity_top_k=5
                )

                # 도구 생성
                tool = QueryEngineTool(
                    query_engine=query_engine,
                    metadata=ToolMetadata(
                        name=name,
                        description=f"{strategy['role']}: {strategy['description']}"
                    ),
                )
                all_tools.append(tool)
                print(f"Successfully created tool for {name}")
                
            except Exception as e:
                print(f"Error creating tool for {name}: {e}")
                continue

    print(f"Total tools created: {len(all_tools)}")
    return all_tools