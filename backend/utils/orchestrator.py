# utils/orchestrator.py
import asyncio
from typing import List, Dict, Any
import time
from utils.qdrant_client import QdrantService
from concurrent.futures import ThreadPoolExecutor
import threading
from utils.collection_strategy import generate_optimized_query, smart_collection_selection, COLLECTION_STRATEGY

class SimpleOrchestrator:
    """순수 검색 전용 오케스트레이터 - 책임 분리"""
    
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
        """순수 검색 기능: 컬렉션별 최적화된 쿼리로 병렬 검색 실행"""
        start_time = time.time()
        
        # 컬렉션별 최적화된 쿼리 생성 (query 파라미터 전달)
        optimized_queries = self._generate_optimized_queries(collections, decomposition, query)
        
        # 🔍 각 컬렉션별 쿼리 로깅
        print("🔍 컬렉션별 최적화된 검색 쿼리:")
        for collection, collection_query in optimized_queries.items():
            print(f"  {collection}: {collection_query[:80]}...")  # 80자만 출력
        
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
    
    def _generate_optimized_queries(self, collections: List[str], decomposition: dict = None, raw_query: str = None) -> dict:
        """컬렉션별 최적화된 쿼리 생성 (전략 문서 기반)"""
        queries = {}
        
        for collection in collections:
            if decomposition:
                # 제품 분해 기반 쿼리 (기존)
                queries[collection] = generate_optimized_query(collection, decomposition)
            elif raw_query:
                # 일반 질문: 증강된 쿼리 활용
                # "Enhanced search query:" 이후 텍스트만 추출
                if "Enhanced search query:" in raw_query:
                    augmented_part = raw_query.split("Enhanced search query:")[1].strip()
                else:
                    augmented_part = raw_query
                
                # 컬렉션 컨텍스트 추가
                strategy = COLLECTION_STRATEGY.get(collection, {})
                context = strategy.get('role', '')
                queries[collection] = f"{context}: {augmented_part}" if context else augmented_part
            else:
                # 폴백: 기본 쿼리
                queries[collection] = "food import export FDA requirements"
        
        return queries
    
    def merge_and_rank(self, parallel_results: dict) -> List[Dict]:
        """순수 검색 기능: 병렬 검색 결과를 병합하고 랭킹"""
        MIN_SCORE = 0.60  # 조정 가능
        QUOTA_PER_COLLECTION = 2
        
        final = []
        collection_stats = {}
        
        for collection, results in parallel_results['results_by_collection'].items():
            # 점수 필터링
            qualified = [r for r in results if r.score >= MIN_SCORE]
            selected = qualified[:QUOTA_PER_COLLECTION]
            
            # 컬렉션 메타정보 가져오기
            collection_info = COLLECTION_STRATEGY.get(collection, {})
            
            # 선택된 항목들을 프론트엔드용 형태로 변환
            for item in selected:
                final.append({
                    "collection": collection,
                    "collection_role": collection_info.get('role', ''),
                    "collection_desc": collection_info.get('description', ''),
                    "score": item.score,
                    "text": item.payload.get("text", "")[:200],
                    "title": item.payload.get("title", ""),
                    "url": item.payload.get("url", "")
                })
            
            collection_stats[collection] = {
                'total': len(results),
                'qualified': len(qualified),
                'selected': len(selected),
                'scores': [r.score for r in selected]
            }
        
        # 디버깅 로그
        print(f"\n📊 균등 랭킹 결과 (최소 점수: {MIN_SCORE})")
        for coll, stats in collection_stats.items():
            print(f"  {coll}: {stats['selected']}개 선발 (점수: {stats['scores']})")
        print(f"📌 총 {len(final)}개, 컬렉션 {len(collection_stats)}개\n")
        
        return sorted(final, key=lambda x: x['score'], reverse=True)
    
    
    def determine_collections(self, decomposition: dict) -> List[str]:
        """순수 검색 기능: 제품 특성에 따른 컬렉션 선택"""
        return smart_collection_selection(decomposition)
    
    def __del__(self):
        """소멸자에서 스레드 풀 정리"""
        if hasattr(self, 'executor'):
            self.executor.shutdown(wait=False)