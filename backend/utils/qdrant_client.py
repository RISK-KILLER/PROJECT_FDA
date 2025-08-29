from qdrant_client import QdrantClient
from qdrant_client.models import Filter, SearchRequest
from openai import OpenAI
import os
from typing import List
import asyncio

class QdrantService:
    def __init__(self):
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60
        )
        self.openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    async def get_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩으로 변환"""
        response = self.openai_client.embeddings.create(
            input=text,
            model="text-embedding-ada-002"
        )
        return response.data[0].embedding
    
    async def search_collection(self, collection_name: str, query: str, limit: int = 5):
        """단일 컬렉션에서 검색"""
        try:
            query_embedding = await self.get_embedding(query)
            
            search_result = self.qdrant_client.search(
                collection_name=collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            return search_result
        except Exception as e:
            print(f"Error searching {collection_name}: {e}")
            return []
    
    async def search_multiple_collections(self, query: str, collections: List[str], limit: int = 3):
        """여러 컬렉션에서 검색"""
        all_results = []
        
        for collection in collections:
            results = await self.search_collection(collection, query, limit)
            for result in results:
                result.collection = collection  # 어느 컬렉션에서 온 결과인지 표시
                all_results.append(result)
        
        # 점수 순으로 정렬
        all_results.sort(key=lambda x: x.score, reverse=True)
        return all_results[:limit * 2]  # 최대 결과 수 제한
