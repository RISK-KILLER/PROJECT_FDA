import json
from typing import List, Dict
import os

class KeywordMapper:
    def __init__(self, mapping_file_path: str = "product_keyword_mappings.json"):
        """BM25 기반 키워드 매핑 시스템 연동"""
        self.mapping_file_path = mapping_file_path
        self.keyword_mappings = self._load_mappings()
        
    def _load_mappings(self) -> Dict:
        """키워드 매핑 파일 로드"""
        try:
            if os.path.exists(self.mapping_file_path):
                with open(self.mapping_file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: {self.mapping_file_path} not found. Using fallback mapping.")
                return {'mappings': {}}
        except Exception as e:
            print(f"Error loading keyword mappings: {e}")
            return {'mappings': {}}
    
    def get_relevant_collections(self, query: str) -> List[str]:
        """쿼리에서 관련 컬렉션 추출"""
        # 제품 감지
        detected_products = self._detect_products(query)
        
        collections = set(['fda_ecfr', 'fda_general'])  # 기본 컬렉션
        
        # BM25 매핑에서 관련 카테고리 추출
        for product in detected_products:
            mapping = self.keyword_mappings['mappings'].get(product, {})
            category = mapping.get('category', '')
            
            # 카테고리에서 컬렉션명 생성
            if category:
                collection_name = f"fda_{category.lower().replace(' ', '_').replace('&', 'and')}"
                collections.add(collection_name)
        
        # 추가 키워드 기반 매핑 (폴백)
        query_lower = query.lower()
        keyword_collections = {
            '라벨': 'fda_labeling',
            'label': 'fda_labeling', 
            '첨가물': 'fda_additives',
            'additive': 'fda_additives',
            '알레르기': 'fda_allergen',
            'allergen': 'fda_allergen',
            '수입': 'fda_imports',
            '수출': 'fda_imports',
            'import': 'fda_imports',
            'export': 'fda_imports'
        }
        
        for keyword, collection in keyword_collections.items():
            if keyword in query_lower:
                collections.add(collection)
        
        return list(collections)
    
    def _detect_products(self, query: str) -> List[str]:
        """쿼리에서 제품 감지"""
        detected = []
        query_lower = query.lower()
        
        # 기본 제품 매핑
        product_mapping = {
            '김치': 'kimchi',
            '라면': 'ramen', 
            '우유': 'milk',
            '치즈': 'cheese',
            '초콜릿': 'chocolate',
            '주스': 'juice'
        }
        
        for korean, english in product_mapping.items():
            if korean in query or english in query_lower:
                # BM25 매핑에 존재하는지 확인
                if english in self.keyword_mappings['mappings']:
                    detected.append(english)
        
        return detected
    
    def get_enhanced_keywords(self, query: str) -> List[str]:
        """쿼리를 BM25 매핑으로 향상"""
        detected_products = self._detect_products(query)
        enhanced_keywords = []
        
        for product in detected_products:
            mapping = self.keyword_mappings['mappings'].get(product, {})
            keywords = mapping.get('keywords', [])
            
            # 상위 키워드만 선택 (신뢰도 0.3 이상)
            for kw in keywords[:5]:
                if kw.get('score', 0) > 0.3:
                    enhanced_keywords.append(kw['term'])
        
        return enhanced_keywords