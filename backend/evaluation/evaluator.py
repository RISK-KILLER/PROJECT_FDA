# evaluation/evaluator.py
"""
LlamaIndex 기반 RAG 평가 시스템
"""

import os
import json
from typing import List, Dict, Any
from datetime import datetime

# LlamaIndex 평가 모듈
from llama_index.core.evaluation import (
    FaithfulnessEvaluator,
    RelevancyEvaluator,
    CorrectnessEvaluator,
    SemanticSimilarityEvaluator
)
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding 


class FDAEvaluator:
    """FDA RAG 시스템 평가기"""
    
    def __init__(self):
        # 평가용 LLM (저렴한 모델)
        self.eval_llm = OpenAI(
            model="gpt-4o-mini",
            temperature=0,
            api_key=os.getenv("OPENAI_API_KEY")
        )

        self.eval_embed_model = OpenAIEmbedding(
            model="text-embedding-3-small",
            api_key=os.getenv("OPENAI_API_KEY")
        )

        # LlamaIndex 평가자 초기화
        self.faithfulness_evaluator = FaithfulnessEvaluator(llm=self.eval_llm)
        self.relevancy_evaluator = RelevancyEvaluator(llm=self.eval_llm)
        self.correctness_evaluator = CorrectnessEvaluator(llm=self.eval_llm)    
        self.similarity_evaluator = SemanticSimilarityEvaluator(
            embed_model=self.eval_embed_model  # llm → embed_model
        )

        # 평가 결과 저장
        self.results = []
        
        # 영어-한국어 키워드 매핑 (FDA 용어)
        self.keyword_translation = {
            # 주요 알레르겐
            "milk": ["우유", "유제품", "milk"],
            "eggs": ["계란", "달걀", "egg", "eggs"],
            "fish": ["생선", "어류", "fish"],
            "shellfish": ["갑각류", "조개류", "shellfish", "crustacean"],
            "nuts": ["견과류", "nuts", "tree nuts"],
            "peanuts": ["땅콩", "peanut", "peanuts"],
            "wheat": ["밀", "소맥", "wheat"],
            "soy": ["콩", "대두", "soy", "soybeans"],
            "sesame": ["참깨", "sesame"],
            "nine": ["9개", "9가지", "아홉", "nine"],
            
            # FDA 규제 용어
            "congress": ["의회", "국회", "congress"],
            "cannot": ["할 수 없", "불가", "금지", "cannot"],
            "statutory": ["법정", "법률", "statutory"],
            "section": ["섹션", "조항", "section"],
            "determined by": ["결정", "정해", "determined"],
            "ingredient list": ["성분 목록", "원재료명", "ingredient"],
            "contains statement": ["함유", "포함", "contains"],
            "declare": ["표시", "명시", "기재", "declare"],
            "labeling": ["라벨", "표시", "표기", "labeling"],
            "import alert": ["수입경보", "수입 경보", "import alert"],
            "detention": ["억류", "detention"],
            "fsvp": ["fsvp", "해외공급업체검증"],
            "foreign supplier": ["해외 공급", "외국 공급", "foreign supplier"],
            "verification": ["검증", "확인", "verification"],
            "importer": ["수입업자", "수입자", "importer"],
            "requirements": ["요구사항", "규정", "요건", "requirements"],
            "registration": ["등록", "registration"],
            "haccp": ["haccp", "해썹"],
        }
    
    def _check_keyword_in_text(self, keyword: str, text: str) -> bool:
        """키워드가 텍스트에 있는지 확인 (한국어 번역 포함)"""
        text_lower = text.lower()
        
        # 1. 영어 키워드 직접 검색
        if keyword.lower() in text_lower:
            return True
        
        # 2. 한국어 번역 검색
        if keyword.lower() in self.keyword_translation:
            translations = self.keyword_translation[keyword.lower()]
            for trans in translations:
                if trans.lower() in text_lower:
                    return True
        
        return False
    
    def evaluate_single(
        self, 
        test_case: Dict[str, Any],
        agent_response: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """단일 테스트 케이스 평가"""
        
        print(f"\n{'='*70}")
        print(f"[{test_case['id']}] {test_case['question']}")
        print(f"{'='*70}")
        
        # 1. Retrieval 평가 (검색 결과가 있는 경우)
        retrieval_metrics = {}
        if retrieved_docs:
            retrieval_metrics = self._evaluate_retrieval(test_case, retrieved_docs)
        
        # 2. Generation 평가
        generation_metrics = self._evaluate_generation(
            test_case,
            agent_response,
            retrieved_docs
        )
        
        # 3. 종합 결과
        result = {
            "test_id": test_case['id'],
            "category": test_case['category'],
            "difficulty": test_case['difficulty'],
            "question": test_case['question'],
            "ground_truth": test_case['ground_truth'],
            
            # Retrieval
            "retrieval": retrieval_metrics,
            
            # Generation
            "generation": generation_metrics,
            
            # 메타
            "timestamp": datetime.now().isoformat(),
            "agent_response": agent_response.get("content", "")[:500]  # 처음 500자만
        }
        
        self.results.append(result)
        
        # 결과 출력
        self._print_single_result(result)
        
        return result
    
    def _evaluate_retrieval(
        self, 
        test_case: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """검색 평가"""
        
        print(f"\n[Retrieval] 평가")
        
        # 기대하는 컬렉션이 검색되었는가?
        expected_collections = set(test_case.get('expected_collections', []))
        retrieved_collections = set(doc.get('collection', '') for doc in retrieved_docs if doc.get('collection'))
        
        collection_precision = len(expected_collections & retrieved_collections) / len(retrieved_collections) if retrieved_collections else 0
        collection_recall = len(expected_collections & retrieved_collections) / len(expected_collections) if expected_collections else 0
        
        # 기대 키워드가 검색 결과에 있는가? (한국어 번역 포함)
        expected_keywords = test_case.get('expected_keywords', [])
        all_text = " ".join([doc.get('text', '') for doc in retrieved_docs])
        
        keyword_hits = sum(1 for kw in expected_keywords if self._check_keyword_in_text(kw, all_text))
        keyword_coverage = keyword_hits / len(expected_keywords) if expected_keywords else 0
        
        # 점수 분포
        scores = [doc.get('score', 0) for doc in retrieved_docs]
        avg_score = sum(scores) / len(scores) if scores else 0
        max_score = max(scores) if scores else 0
        
        metrics = {
            "total_docs": len(retrieved_docs),
            "collection_precision": round(collection_precision, 3),
            "collection_recall": round(collection_recall, 3),
            "keyword_coverage": round(keyword_coverage, 3),
            "avg_score": round(avg_score, 3),
            "max_score": round(max_score, 3),
            "retrieved_collections": list(retrieved_collections)
        }
        
        print(f"  - 검색 문서: {metrics['total_docs']}개")
        print(f"  - Collection Precision: {metrics['collection_precision']:.2%}")
        print(f"  - Keyword Coverage: {metrics['keyword_coverage']:.2%}")
        print(f"  - Avg Score: {metrics['avg_score']:.3f}")
        
        return metrics
    
    def _evaluate_generation(
        self,
        test_case: Dict[str, Any],
        agent_response: Dict[str, Any],
        retrieved_docs: List[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """답변 생성 평가"""
        
        print(f"\n[Generation] 평가")
        
        query = test_case['question']
        response = agent_response.get("content", "")
        reference = test_case['ground_truth']
        
        # 1. Faithfulness (문서 충실도) - 검색 문서가 있는 경우만
        faithfulness_score = 0.0
        if retrieved_docs:
            try:
                contexts = [doc.get('text', '') for doc in retrieved_docs[:5]]
                
                faithfulness_result = self.faithfulness_evaluator.evaluate(
                    query=query,
                    response=response,
                    contexts=contexts
                )
                faithfulness_score = faithfulness_result.score if faithfulness_result.score else 0.0
                
                print(f"  - Faithfulness: {faithfulness_score:.2f}")
                
            except Exception as e:
                print(f"  [경고] Faithfulness 평가 실패: {e}")
        
        # 2. Relevancy (답변 관련성)
        relevancy_score = 0.0
        try:
            # contexts 파라미터 추가
            contexts = [doc.get('text', '') for doc in retrieved_docs[:5]] if retrieved_docs else []
            relevancy_result = self.relevancy_evaluator.evaluate(
                query=query,
                response=response,
                contexts=contexts
            )
            relevancy_score = relevancy_result.score if relevancy_result.score else 0.0
            
            print(f"  - Relevancy: {relevancy_score:.2f}")
            
        except Exception as e:
            print(f"  [경고] Relevancy 평가 실패: {e}")
        
        # 3. Correctness (정확성)
        correctness_score = 0.0
        try:
            correctness_result = self.correctness_evaluator.evaluate(
                query=query,
                response=response,
                reference=reference
            )
            # Correctness는 1-5 스케일이므로 0-1로 정규화
            raw_score = correctness_result.score if correctness_result.score else 0.0
            correctness_score = (raw_score - 1) / 4 if raw_score > 0 else 0.0  # 1-5 → 0-1
            
            print(f"  - Correctness: {correctness_score:.2f} (raw: {raw_score:.1f}/5)")
            
        except Exception as e:
            print(f"  [경고] Correctness 평가 실패: {e}")
        
        # 4. Semantic Similarity (의미 유사도)
        similarity_score = 0.0
        try:
            similarity_result = self.similarity_evaluator.evaluate(
                query=query,
                response=response,
                reference=reference
            )
            similarity_score = similarity_result.score if similarity_result.score else 0.0
            
            print(f"  - Semantic Similarity: {similarity_score:.2f}")
            
        except Exception as e:
            print(f"  [경고] Similarity 평가 실패: {e}")
        
        # 5. 추가: 키워드 기반 간단 체크 (한국어 번역 포함)
        expected_keywords = test_case.get('expected_keywords', [])
        keyword_hits = sum(1 for kw in expected_keywords if self._check_keyword_in_text(kw, response))
        keyword_coverage = keyword_hits / len(expected_keywords) if expected_keywords else 0
        
        print(f"  - Keyword Coverage (답변): {keyword_coverage:.2%}")
        if keyword_coverage > 0:
            matched_keywords = [kw for kw in expected_keywords if self._check_keyword_in_text(kw, response)]
            print(f"    매칭된 키워드: {matched_keywords}")
        
        return {
            "faithfulness": round(faithfulness_score, 3),
            "relevancy": round(relevancy_score, 3),
            "correctness": round(correctness_score, 3),
            "similarity": round(similarity_score, 3),
            "keyword_coverage": round(keyword_coverage, 3),
            "response_length": len(response)
        }
    
    def _print_single_result(self, result: Dict[str, Any]):
        """단일 결과 출력"""
        
        print(f"\n[완료] 평가 완료")
        print(f"  - Correctness: {result['generation']['correctness']:.2f}")
        print(f"  - Faithfulness: {result['generation']['faithfulness']:.2f}")
        print(f"  - Keyword Coverage: {result['generation']['keyword_coverage']:.2%}")
        
        if result['retrieval']:
            print(f"  - Retrieved: {result['retrieval']['total_docs']}개")
        
        print()
    
    def generate_report(self) -> Dict[str, Any]:
        """전체 평가 리포트 생성"""
        
        if not self.results:
            return {"error": "No evaluation results"}
        
        # 카테고리별 집계
        by_category = {}
        for result in self.results:
            cat = result['category']
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(result)
        
        # 전체 평균
        def safe_avg(items, key):
            values = [item[key] for item in items if item.get(key) is not None]
            return sum(values) / len(values) if values else 0
        
        generation_metrics = [r['generation'] for r in self.results]
        retrieval_metrics = [r['retrieval'] for r in self.results if r.get('retrieval')]
        
        overall_metrics = {
            "correctness": safe_avg(generation_metrics, 'correctness'),
            "faithfulness": safe_avg(generation_metrics, 'faithfulness'),
            "relevancy": safe_avg(generation_metrics, 'relevancy'),
            "similarity": safe_avg(generation_metrics, 'similarity'),
            "keyword_coverage": safe_avg(generation_metrics, 'keyword_coverage'),
        }
        
        if retrieval_metrics:
            overall_metrics.update({
                "avg_retrieved_docs": safe_avg(retrieval_metrics, 'total_docs'),
                "collection_precision": safe_avg(retrieval_metrics, 'collection_precision'),
                "keyword_coverage_retrieval": safe_avg(retrieval_metrics, 'keyword_coverage'),
            })
        
        # 카테고리별 성능
        category_performance = {}
        for cat, results in by_category.items():
            gen_metrics = [r['generation'] for r in results]
            category_performance[cat] = {
                "count": len(results),
                "correctness": safe_avg(gen_metrics, 'correctness'),
                "faithfulness": safe_avg(gen_metrics, 'faithfulness'),
            }
        
        return {
            "summary": {
                "total_tests": len(self.results),
                "timestamp": datetime.now().isoformat()
            },
            "overall_metrics": overall_metrics,
            "by_category": category_performance,
            "detailed_results": self.results
        }
    
    def save_report(self, filename: str):
        """리포트 저장"""
        
        report = self.generate_report()
        
        os.makedirs("evaluation/results", exist_ok=True)
        filepath = f"evaluation/results/{filename}"
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        print(f"\n💾 리포트 저장: {filepath}")
        
        return filepath