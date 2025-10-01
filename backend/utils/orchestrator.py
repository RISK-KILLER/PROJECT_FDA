# utils/orchestrator.py
import asyncio
from typing import List, Dict, Any
import time
from utils.qdrant_client import QdrantService
from concurrent.futures import ThreadPoolExecutor
import threading
from utils.collection_strategy import generate_optimized_query, smart_collection_selection, COLLECTION_STRATEGY

class SimpleOrchestrator:
    """병렬 검색을 위한 오케스트레이터"""
    
    def __init__(self):
        self.qdrant_service = QdrantService()
        # 스레드 풀 생성
        self.executor = ThreadPoolExecutor(max_workers=10)
    
    def _search_collection_sync(self, collection: str, query: str, limit: int = 5):
        """동기식 검색 (스레드에서 실행용)"""
        try:
            # 새 이벤트 루프 생성 (각 스레드별로)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(
                    self.qdrant_service.search_collection(collection, query, limit)
                )
                return result
            finally:
                loop.close()
        except Exception as e:
            print(f"Error in {collection}: {e}")
            return []
    
    def parallel_search(self, query: str, collections: List[str], decomposition: dict = None) -> Dict[str, Any]:
        """컬렉션별 최적화된 쿼리로 병렬 검색"""
        start_time = time.time()
        
        # 컬렉션별 최적화된 쿼리 생성
        optimized_queries = self._generate_optimized_queries(collections, decomposition)
        
        # 🔍 각 컬렉션별 쿼리 로깅
        print("🔍 컬렉션별 최적화된 검색 쿼리:")
        for collection, collection_query in optimized_queries.items():
            print(f"  {collection}: {collection_query}")
        
        futures = []
        for collection in collections:
            # 각 컬렉션에 맞는 쿼리 사용
            collection_query = optimized_queries.get(collection, query)
            future = self.executor.submit(
                self._search_collection_sync,
                collection,
                collection_query,
                5
            )
            futures.append((collection, future))
        
        # 결과 수집
        combined = {
            "search_time": time.time() - start_time,
            "results_by_collection": {}
        }
        
        print("📊 컬렉션별 검색 결과:")
        for collection, future in futures:
            try:
                result = future.result(timeout=10)  # 10초 타임아웃
                combined["results_by_collection"][collection] = result
                
                # 📊 검색 결과 점수 분포 확인
                if result:
                    scores = [r.score for r in result]
                    print(f"  {collection}: {len(result)}개 결과, 점수: {[f'{s:.3f}' for s in scores[:3]]}")
                else:
                    print(f"  {collection}: 0개 결과")
                    
            except Exception as e:
                print(f"Error getting result for {collection}: {e}")
                combined["results_by_collection"][collection] = []
                print(f"  {collection}: 오류 발생")
        
        combined["search_time"] = time.time() - start_time
        return combined
    
    def _generate_optimized_queries(self, collections: List[str], decomposition: dict = None) -> dict:
        """컬렉션별 최적화된 쿼리 생성 (전략 문서 기반)"""
        queries = {}
        
        for collection in collections:
            if decomposition:
                queries[collection] = generate_optimized_query(collection, decomposition)
            else:
                # decomposition이 없으면 기본 쿼리
                queries[collection] = "food import export FDA requirements"
        
        return queries
    
    def merge_and_rank(self, results: Dict[str, Any], min_score: float = 0.3) -> List[Dict]:
        """가중치 없는 투명한 결과 병합 - 순수 점수만 사용"""
        all_items = []
        
        for collection, items in results.get("results_by_collection", {}).items():
            if items:
                # 컬렉션 메타정보 가져오기
                collection_info = COLLECTION_STRATEGY.get(collection, {})
                
                for item in items:
                    # 최소 점수 필터링만 적용
                    if item.score < min_score:
                        continue
                    
                    all_items.append({
                        "collection": collection,
                        "collection_role": collection_info.get('role', ''),  # 🚫, 📏, 📋 등
                        "collection_desc": collection_info.get('description', ''),
                        "score": item.score,  # 가중치 없는 원래 점수
                        "text": item.payload.get("text", "")[:200],
                        "title": item.payload.get("title", ""),
                        "url": item.payload.get("url", "")
                    })
        
        # 순수 벡터 유사도 점수로만 정렬
        all_items.sort(key=lambda x: x["score"], reverse=True)
        return all_items[:10]
    
    
    def determine_collections(self, decomposition: dict) -> List[str]:
        """제품 특성에 따른 컬렉션 선택 (실제 7개 컬렉션 기반)"""
        return smart_collection_selection(decomposition)
    
    def __del__(self):
        """소멸자에서 스레드 풀 정리"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)