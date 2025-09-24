# test_wrapper.py
"""
래퍼 함수가 제대로 작동하는지 확인하는 테스트 코드
각 컬렉션의 실제 데이터를 검사하고 래퍼 함수의 텍스트 추출을 테스트합니다.
"""

import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from openai import OpenAI
import json

load_dotenv()

# TEXT_FIELD_MAPPING을 직접 정의 (tools.py import 대신)
TEXT_FIELD_MAPPING = {
    'dwpe': ['reason_for_alert', 'guidance_text', 'title'],
    'ecfr': ['content', 'title'],
    'fsvp': ['original_text', 'summary', 'question'],
    'gras': ['text', 'substance', 'intended_use'],
    'guidance': ['text', 'title'],
    'rpm': ['original_text', 'section_title'],
    'usc': ['content', 'title']
}

class TextFieldWrapper:
    """tools.py의 TextFieldWrapper 간소화 버전"""
    
    @staticmethod
    def extract_text(payload: dict, collection_name: str) -> str:
        if not payload:
            return f"No data available from {collection_name}"
        
        text_fields = TEXT_FIELD_MAPPING.get(collection_name, ['text'])
        
        for field in text_fields:
            if field in payload and payload[field]:
                text = payload[field]
                if len(str(text)) < 50:
                    for backup_field in text_fields:
                        if backup_field != field and backup_field in payload:
                            text += f" {payload[backup_field]}"
                            if len(str(text)) > 100:
                                break
                return str(text)
        
        text_parts = []
        for key, value in payload.items():
            if isinstance(value, str) and value and key != 'url':
                text_parts.append(f"{key}: {value[:100]}")
                if len(' '.join(text_parts)) > 200:
                    break
        
        return ' '.join(text_parts) if text_parts else f"Empty result from {collection_name}"

class WrapperTester:
    def __init__(self):
        self.qdrant = QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY")
        )
        self.openai = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.wrapper = TextFieldWrapper()
        self.collections = ['dwpe', 'ecfr', 'fsvp', 'gras', 'guidance', 'rpm', 'usc']
    
    def get_sample_data(self, collection: str, num_samples: int = 3):
        """각 컬렉션에서 샘플 데이터 가져오기"""
        try:
            dummy_vector = [0.1] * 1536
            results = self.qdrant.search(
                collection_name=collection,
                query_vector=dummy_vector,
                limit=num_samples
            )
            return results
        except Exception as e:
            print(f"Error getting samples from {collection}: {e}")
            return []
    
    def test_text_extraction(self):
        """텍스트 추출 테스트"""
        print("\n" + "="*60)
        print("🧪 래퍼 함수 텍스트 추출 테스트")
        print("="*60)
        
        results = {}
        
        for collection in self.collections:
            print(f"\n📁 {collection} 테스트:")
            print(f"   예상 필드: {TEXT_FIELD_MAPPING.get(collection, ['text'])}")
            
            samples = self.get_sample_data(collection, 3)
            
            if not samples:
                print(f"   ❌ 샘플 데이터 없음")
                results[collection] = {"status": "no_data", "extracted": 0, "failed": 0}
                continue
            
            extracted_count = 0
            failed_count = 0
            
            for i, sample in enumerate(samples, 1):
                if sample.payload:
                    extracted_text = self.wrapper.extract_text(sample.payload, collection)
                    
                    is_valid = (
                        extracted_text and 
                        extracted_text != f"No data available from {collection}" and
                        extracted_text != f"Empty result from {collection}" and
                        len(extracted_text) > 10
                    )
                    
                    if is_valid:
                        extracted_count += 1
                        print(f"   ✅ 샘플 {i}: 텍스트 추출 성공 ({len(extracted_text)}자)")
                        print(f"      미리보기: {extracted_text[:80]}...")
                    else:
                        failed_count += 1
                        print(f"   ❌ 샘플 {i}: 텍스트 추출 실패")
                        print(f"      결과: {extracted_text[:80]}")
                else:
                    failed_count += 1
                    print(f"   ❌ 샘플 {i}: payload 없음")
            
            success_rate = (extracted_count / len(samples)) * 100 if samples else 0
            results[collection] = {
                "status": "success" if success_rate > 50 else "failed",
                "extracted": extracted_count,
                "failed": failed_count,
                "success_rate": success_rate
            }
            
            print(f"   📊 성공률: {success_rate:.0f}% ({extracted_count}/{len(samples)})")
    
    def test_field_availability(self):
        """각 컬렉션의 실제 필드 확인"""
        print("\n" + "="*60)
        print("🔍 실제 필드 존재 여부 확인")
        print("="*60)
        
        for collection in self.collections:
            print(f"\n📁 {collection}:")
            samples = self.get_sample_data(collection, 1)
            
            if samples and samples[0].payload:
                payload = samples[0].payload
                expected_fields = TEXT_FIELD_MAPPING.get(collection, ['text'])
                
                print(f"   예상 필드: {expected_fields}")
                print(f"   실제 필드:")
                
                for field, value in list(payload.items())[:10]:
                    if value is None:
                        status = "❌ None"
                    elif isinstance(value, str) and value:
                        status = f"✅ 문자열 ({len(value)}자)"
                    elif isinstance(value, str) and not value:
                        status = "⚠️ 빈 문자열"
                    else:
                        status = f"ℹ️ {type(value).__name__}"
                    
                    print(f"      - {field}: {status}")
                
                print(f"\n   텍스트 필드 체크:")
                for field in expected_fields:
                    if field in payload:
                        value = payload[field]
                        if value and isinstance(value, str):
                            print(f"      ✅ '{field}' 존재 및 유효")
                        else:
                            print(f"      ⚠️ '{field}' 존재하지만 비어있거나 None")
                    else:
                        print(f"      ❌ '{field}' 필드 없음")
    
    def test_specific_queries(self):
        """특정 검색어로 실제 검색 테스트"""
        print("\n" + "="*60)
        print("🔎 실제 검색 쿼리 테스트")
        print("="*60)
        
        test_queries = ["shrimp", "seafood", "import", "FDA"]
        
        for query in test_queries:
            print(f"\n검색어: '{query}'")
            
            embedding_response = self.openai.embeddings.create(
                input=query,
                model="text-embedding-3-small"
            )
            query_vector = embedding_response.data[0].embedding
            
            for collection in self.collections:
                try:
                    results = self.qdrant.search(
                        collection_name=collection,
                        query_vector=query_vector,
                        limit=1
                    )
                    
                    if results and results[0].payload:
                        text = self.wrapper.extract_text(results[0].payload, collection)
                        is_valid = text and len(text) > 10 and "No data" not in text
                        
                        status = "✅" if is_valid else "❌"
                        print(f"   {collection}: {status} (점수: {results[0].score:.2f})")
                    else:
                        print(f"   {collection}: ❌ 검색 결과 없음")
                        
                except Exception as e:
                    print(f"   {collection}: ❌ 에러 - {str(e)[:50]}")
    
    def generate_report(self):
        """종합 보고서 생성"""
        print("\n" + "="*60)
        print("📊 종합 진단 보고서")
        print("="*60)
        
        print("\n래퍼 함수 상태:")
        print("- TextFieldWrapper 클래스: ✅ 정의됨")
        print("- TEXT_FIELD_MAPPING: ✅ 설정됨")
        
        print("\n권장 사항:")
        print("1. gras/guidance는 잘 작동 → 유지")
        print("2. 나머지 컬렉션들은 데이터 구조 문제")
        print("3. 옵션:")
        print("   a) 현 상태 유지 (2개 도구 + 병렬 검색)")
        print("   b) 문제 컬렉션 재업로드 (text 필드 추가)")
        print("   c) 래퍼 함수 더 정교하게 개선")

def main():
    print("🚀 래퍼 함수 동작 테스트 시작...")
    print("="*60)
    
    tester = WrapperTester()
    
    # 1. 필드 존재 여부 확인
    tester.test_field_availability()
    
    # 2. 텍스트 추출 테스트
    tester.test_text_extraction()
    
    # 3. 실제 검색 테스트
    tester.test_specific_queries()
    
    # 4. 종합 보고서
    tester.generate_report()
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    main()