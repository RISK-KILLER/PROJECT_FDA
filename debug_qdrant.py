# debug_qdrant.py
"""
FDA Qdrant 컬렉션 디버깅 도구
각 컬렉션의 데이터 존재 여부와 검색 패턴을 확인합니다.
"""

import os
import json
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from openai import OpenAI
from typing import List, Dict

# 환경 변수 로드
load_dotenv()

class QdrantDebugger:
    def __init__(self):
        self.qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.collections = ['dwpe', 'ecfr', 'fsvp', 'gras', 'guidance', 'rpm', 'usc']
    
    def get_embedding(self, text: str) -> List[float]:
        """텍스트를 임베딩으로 변환"""
        response = self.openai.embeddings.create(
            input=text,
            model="text-embedding-3-small"  # 중요: 업로드와 동일한 모델
        )
        return response.data[0].embedding
    
    def check_collection_info(self):
        """각 컬렉션의 기본 정보 확인"""
        print("\n" + "="*50)
        print("📊 컬렉션 기본 정보")
        print("="*50)
        
        for collection in self.collections:
            try:
                info = self.qdrant.get_collection(collection)
                print(f"\n{collection}:")
                print(f"  - 포인트 개수: {info.points_count}")
                print(f"  - 벡터 차원: {info.config.params.vectors.size}")
                print(f"  - 상태: ✅ 정상")
            except Exception as e:
                print(f"\n{collection}:")
                print(f"  - 상태: ❌ 에러 - {e}")
    
    def test_search_patterns(self):
        """다양한 검색 패턴 테스트"""
        print("\n" + "="*50)
        print("🔍 검색 패턴 테스트")
        print("="*50)
        
        # 테스트할 검색어들
        test_queries = {
            "specific": ["canned peaches", "peaches", "복숭아 통조림"],
            "general": ["canned fruit", "fruit", "food", "Korea"],
            "regulatory": ["import", "export", "FDA", "requirements"],
            "empty": [""]  # 빈 검색어 테스트
        }
        
        results = {}
        
        for collection in self.collections:
            print(f"\n📁 {collection} 컬렉션 테스트:")
            results[collection] = {}
            
            for category, queries in test_queries.items():
                for query in queries:
                    if not query:  # 빈 검색어 스킵
                        continue
                    
                    try:
                        embedding = self.get_embedding(query)
                        search_results = self.qdrant.search(
                            collection_name=collection,
                            query_vector=embedding,
                            limit=5
                        )
                        
                        # 결과 분석
                        count = len(search_results)
                        has_text = False
                        none_count = 0
                        
                        for result in search_results:
                            if result.payload and result.payload.get('text'):
                                has_text = True
                            elif result.payload and result.payload.get('text') is None:
                                none_count += 1
                        
                        status = "✅" if count > 0 and has_text else "⚠️" if count > 0 else "❌"
                        print(f"  [{category}] '{query[:20]}': {status} {count}개 (None: {none_count}개)")
                        
                        results[collection][query] = {
                            "count": count,
                            "has_text": has_text,
                            "none_count": none_count
                        }
                        
                    except Exception as e:
                        print(f"  [{category}] '{query[:20]}': ❌ 에러 - {str(e)[:50]}")
    
    def analyze_data_structure(self):
        """각 컬렉션의 데이터 구조 분석"""
        print("\n" + "="*50)
        print("🏗️ 데이터 구조 분석")
        print("="*50)
        
        for collection in self.collections:
            try:
                # 샘플 데이터 가져오기 (임의의 벡터로 검색)
                sample_vector = [0.1] * 1536  # 임의의 벡터
                samples = self.qdrant.search(
                    collection_name=collection,
                    query_vector=sample_vector,
                    limit=3
                )
                
                if samples:
                    print(f"\n{collection} 샘플 데이터:")
                    for i, sample in enumerate(samples[:1], 1):  # 첫 번째 샘플만
                        if sample.payload:
                            print(f"  필드들:")
                            for key in list(sample.payload.keys())[:5]:  # 상위 5개 필드
                                value = sample.payload.get(key)
                                value_type = type(value).__name__
                                
                                # 값 미리보기
                                if value is None:
                                    preview = "None"
                                elif isinstance(value, str):
                                    preview = value[:30] + "..." if len(value) > 30 else value
                                elif isinstance(value, list):
                                    preview = f"[{len(value)} items]"
                                else:
                                    preview = str(value)[:30]
                                
                                print(f"    - {key}: {value_type} = {preview}")
                else:
                    print(f"\n{collection}: 데이터 없음")
                    
            except Exception as e:
                print(f"\n{collection}: 에러 - {e}")
    
    def find_problem_root_cause(self):
        """문제의 근본 원인 분석"""
        print("\n" + "="*50)
        print("💡 문제 근본 원인 분석")
        print("="*50)
        
        # 특정 쿼리로 각 컬렉션 테스트
        test_query = "canned peaches"
        embedding = self.get_embedding(test_query)
        
        working_collections = []
        failing_collections = []
        
        for collection in self.collections:
            try:
                results = self.qdrant.search(
                    collection_name=collection,
                    query_vector=embedding,
                    limit=1
                )
                
                if results and results[0].payload and results[0].payload.get('text'):
                    working_collections.append(collection)
                else:
                    failing_collections.append(collection)
                    
            except:
                failing_collections.append(collection)
        
        print(f"\n✅ 작동하는 컬렉션 ({len(working_collections)}개):")
        for col in working_collections:
            print(f"  - {col}")
        
        print(f"\n❌ 문제 있는 컬렉션 ({len(failing_collections)}개):")
        for col in failing_collections:
            print(f"  - {col}")
        
        # 원인 진단
        print("\n🔬 진단 결과:")
        if failing_collections:
            print(f"  1. {failing_collections} 컬렉션들은 'canned peaches'와 같은")
            print(f"     구체적인 제품명을 포함하지 않는 것으로 보입니다.")
            print(f"  2. 이들은 더 일반적인 용어(import, food, Korea 등)로")
            print(f"     검색해야 할 가능성이 높습니다.")
            print(f"  3. 또는 text 필드가 다른 이름으로 저장되었을 수 있습니다.")

def main():
    """메인 실행 함수"""
    print("🔧 FDA Qdrant 디버깅 시작...")
    print("="*60)
    
    debugger = QdrantDebugger()
    
    # 1. 컬렉션 정보 확인
    debugger.check_collection_info()
    
    # 2. 검색 패턴 테스트
    debugger.test_search_patterns()
    
    # 3. 데이터 구조 분석
    debugger.analyze_data_structure()
    
    # 4. 근본 원인 분석
    debugger.find_problem_root_cause()
    
    print("\n" + "="*60)
    print("✅ 디버깅 완료!")

if __name__ == "__main__":
    main()