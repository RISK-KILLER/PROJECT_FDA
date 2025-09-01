# utils/rag_engine.py
"""
LlamaIndex 0.11.x를 활용한 RAG 엔진
FDA 규제 문서 검색 및 답변 생성
"""

import os
from typing import List, Dict, Optional
from dotenv import load_dotenv

# LlamaIndex 0.11.x imports
from llama_index.core import VectorStoreIndex, Settings
from llama_index.core.schema import NodeWithScore, TextNode
from llama_index.core.response_synthesizers import get_response_synthesizer
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.openai import OpenAI
from qdrant_client import QdrantClient
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

class FDARAGEngine:
    def __init__(self):
        """RAG 엔진 초기화"""
        # Qdrant 클라이언트 설정
        self.qdrant_client = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
            timeout=60
        )
        
        # LlamaIndex 설정
        self.embed_model = OpenAIEmbedding(
            model="text-embedding-ada-002",
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        self.llm = OpenAI(
            model="gpt-3.5-turbo",
            temperature=0.1,
            api_key=os.getenv("OPENAI_API_KEY")
        )
        
        # Global settings for LlamaIndex 0.11.x
        Settings.embed_model = self.embed_model
        Settings.llm = self.llm
        Settings.chunk_size = 512
        
        # 시스템 프롬프트
        self.system_prompt = """당신은 FDA 식품 수출 규제 전문가입니다. 
        한국 중소기업이 미국으로 식품을 수출할 때 필요한 FDA 규제 정보를 정확하고 실용적으로 제공합니다.
        
        답변 시 다음 사항을 준수하세요:
        1. FDA 공식 문서를 기반으로 정확한 정보만 제공
        2. 관련 CFR (Code of Federal Regulations) 조항 명시
        3. 실제 적용 가능한 구체적인 가이드라인 제시
        4. 불확실한 정보는 명확히 구분하여 설명
        5. 한국어로 답변하되, 규제 용어는 영문 병기
        """
        
        # 컬렉션별 인덱스 캐시
        self.index_cache = {}
        
    def get_or_create_index(self, collection_name: str) -> VectorStoreIndex:
        """컬렉션에 대한 인덱스 생성 또는 캐시에서 반환"""
        if collection_name not in self.index_cache:
            try:
                vector_store = QdrantVectorStore(
                    client=self.qdrant_client,
                    collection_name=collection_name,
                    embed_model=self.embed_model
                )
                
                # 기존 벡터 스토어에서 인덱스 생성
                index = VectorStoreIndex.from_vector_store(
                    vector_store=vector_store,
                    embed_model=self.embed_model
                )
                
                self.index_cache[collection_name] = index
                logger.info(f"Index created for collection: {collection_name}")
                
            except Exception as e:
                logger.error(f"Error creating index for {collection_name}: {e}")
                return None
                
        return self.index_cache[collection_name]
    
    def search_collection(
        self, 
        collection_name: str, 
        query: str, 
        top_k: int = 3
    ) -> List[NodeWithScore]:
        """단일 컬렉션에서 검색"""
        index = self.get_or_create_index(collection_name)
        if not index:
            return []
        
        try:
            # 0.11.x에서는 as_query_engine 사용
            query_engine = index.as_query_engine(
                similarity_top_k=top_k,
                response_mode="no_text"  # 검색만 수행
            )
            
            response = query_engine.query(query)
            return response.source_nodes if response.source_nodes else []
            
        except Exception as e:
            logger.error(f"Error searching {collection_name}: {e}")
            return []
    
    def multi_collection_search(
        self,
        query: str,
        collections: List[str],
        top_k_per_collection: int = 3
    ) -> List[NodeWithScore]:
        """여러 컬렉션에서 통합 검색"""
        all_results = []
        
        for collection in collections:
            results = self.search_collection(collection, query, top_k_per_collection)
            
            # 컬렉션 정보를 메타데이터에 추가
            for node in results:
                if hasattr(node, 'node') and hasattr(node.node, 'metadata'):
                    node.node.metadata['source_collection'] = collection
                all_results.extend(results)
        
        # 점수순 정렬
        all_results.sort(key=lambda x: x.score if hasattr(x, 'score') else 0, reverse=True)
        
        return all_results[:top_k_per_collection * 2]  # 상위 결과만 반환
    
    def generate_response(
        self,
        query: str,
        search_results: List[NodeWithScore],
        include_checklist: bool = True
    ) -> Dict:
        """검색 결과를 바탕으로 응답 생성"""
        
        if not search_results:
            return {
                "content": "죄송합니다. 해당 질문에 대한 FDA 규제 정보를 찾을 수 없습니다. 다른 키워드로 검색해 주세요.",
                "sources": [],
                "cfr_references": [],
                "keywords": []
            }
        
        # 컨텍스트 구성
        context_parts = []
        sources = []
        cfr_references = []
        
        for i, node in enumerate(search_results[:5], 1):
            # 노드 텍스트 추출
            text = node.node.text if hasattr(node.node, 'text') else str(node.node)
            metadata = node.node.metadata if hasattr(node.node, 'metadata') else {}
            
            context_parts.append(f"[문서 {i}]\n제목: {metadata.get('title', 'N/A')}\n내용: {text[:500]}...")
            
            # 소스 정보 수집
            if metadata.get('title'):
                sources.append({
                    'title': metadata.get('title'),
                    'category': metadata.get('category', ''),
                    'url': metadata.get('url', '')
                })
            
            # CFR 참조 수집
            if metadata.get('has_cfr'):
                cfr_references.append({
                    'title': metadata.get('title', ''),
                    'description': f"카테고리: {metadata.get('category', '')}",
                    'url': metadata.get('url', '')
                })
        
        context = "\n\n".join(context_parts)
        
        # 프롬프트 구성
        checklist_section = "4. **체크리스트**: 확인해야 할 항목들" if include_checklist else ""
        
        prompt = f"""{self.system_prompt}

검색된 FDA 문서:
{context}

사용자 질문: {query}

위 문서를 바탕으로 다음 형식으로 답변해주세요:

1. **핵심 답변**: 질문에 대한 직접적인 답변
2. **관련 FDA 규제**: 적용되는 구체적인 규제 사항
3. **필요 조치사항**: 수출업체가 준수해야 할 사항
{checklist_section}

답변:"""

        # LLM 응답 생성
        try:
            response = self.llm.complete(prompt)
            response_text = response.text if hasattr(response, 'text') else str(response)
        except Exception as e:
            logger.error(f"Error generating LLM response: {e}")
            response_text = "응답 생성 중 오류가 발생했습니다."
        
        # 키워드 추출 (간단한 구현)
        keywords = self._extract_keywords(query, response_text)
        
        return {
            "content": response_text,
            "sources": sources,
            "cfr_references": cfr_references[:3],  # 상위 3개만
            "keywords": keywords
        }
    
    def _extract_keywords(self, query: str, response: str) -> List[str]:
        """쿼리와 응답에서 주요 키워드 추출"""
        keywords = []
        
        # 제품 관련 키워드
        product_keywords = {
            '김치': ['fermented', 'acidified', 'vegetable'],
            '라면': ['processed_grain', 'noodle', 'instant'],
            '우유': ['dairy', 'milk', 'pasteurized'],
            '치즈': ['dairy', 'cheese', 'aged'],
            '수산물': ['seafood', 'fish', 'HACCP'],
            '과자': ['bakery', 'snack', 'processed']
        }
        
        # 규제 관련 키워드
        regulation_keywords = {
            '라벨': ['labeling', 'nutrition_facts'],
            '첨가물': ['additives', 'GRAS'],
            '알레르기': ['allergen', 'warning'],
            'HACCP': ['HACCP', 'food_safety'],
            '수입': ['import', 'prior_notice']
        }
        
        # 쿼리에서 키워드 매칭
        query_lower = query.lower()
        for korean, eng_keywords in {**product_keywords, **regulation_keywords}.items():
            if korean in query:
                keywords.extend(eng_keywords[:2])
        
        return list(set(keywords))[:5]  # 중복 제거, 최대 5개
    
    def query(
        self,
        query: str,
        collections: Optional[List[str]] = None,
        include_checklist: bool = True
    ) -> Dict:
        """
        통합 쿼리 인터페이스
        
        Args:
            query: 사용자 질문
            collections: 검색할 컬렉션 리스트 (None이면 자동 선택)
            include_checklist: 체크리스트 포함 여부
            
        Returns:
            응답 딕셔너리
        """
        # <<-- [테스트용 수정] 검색할 컬렉션 목록을 여기에 직접 지정합니다.
        healthy_collections = [
            'fda_additives',
            'fda_ecfr',
            'fda_usc',
            'fda_labeling',
            'fda_allergen'
        ]
        
        # main.py에서 어떤 값을 전달하든, 위 목록으로 강제 설정합니다.
        collections = healthy_collections
        
        # 원래의 자동 선택 로직은 잠시 주석 처리합니다.
        # if not collections:
        #     collections = self._auto_select_collections(query)
        
        logger.info(f"Searching in TEST collections (hardcoded): {collections}")
        
        # 검색 수행
        search_results = self.multi_collection_search(
            query=query,
            collections=collections,
            top_k_per_collection=3
        )
        
        # 응답 생성
        response = self.generate_response(
            query=query,
            search_results=search_results,
            include_checklist=include_checklist
        )
        
        return response
    
    def _auto_select_collections(self, query: str) -> List[str]:
        """쿼리에 따라 관련 컬렉션 자동 선택"""
        collections = ['fda_ecfr', 'fda_general']  # 기본 컬렉션
        
        query_lower = query.lower()
        
        # 제품별 컬렉션 매핑
        if '김치' in query or 'kimchi' in query_lower:
            collections.extend(['fda_vegetables', 'fda_condiment_industry'])
        if '라면' in query or 'ramen' in query_lower or 'noodle' in query_lower:
            collections.append('fda_processed_grain')
        if '우유' in query or 'milk' in query_lower:
            collections.append('fda_dairy')
        if '치즈' in query or 'cheese' in query_lower:
            collections.append('fda_dairy')
        if '수산' in query or 'seafood' in query_lower or 'fish' in query_lower:
            collections.append('fda_fish_and_seafood')
        
        # 주제별 컬렉션 매핑
        if '라벨' in query or 'label' in query_lower:
            collections.append('fda_labeling')
        if '첨가' in query or 'additive' in query_lower:
            collections.append('fda_additives')
        if '알레르기' in query or 'allergen' in query_lower:
            collections.append('fda_allergen')
        if '수입' in query or '수출' in query or 'import' in query_lower or 'export' in query_lower:
            collections.append('fda_imports')
        
        return list(set(collections))  # 중복 제거