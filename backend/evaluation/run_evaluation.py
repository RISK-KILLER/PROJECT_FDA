# evaluation/run_evaluation.py
"""
평가 실행 스크립트
"""

import sys
sys.path.append('..')

from evaluation.test_dataset import get_dataset
from evaluation.evaluator import FDAEvaluator
from utils.agent import FDAAgent
from datetime import datetime


def run_evaluation(version_name: str = "baseline"):
    """평가 실행"""
    
    print("="*80)
    print(f"🧪 FDA RAG 시스템 평가 - {version_name}")
    print("="*80)
    
    # Agent 초기화
    agent = FDAAgent()
    evaluator = FDAEvaluator()
    
    # 테스트 데이터셋 로드
    test_dataset = get_dataset()
    
    print(f"\n📝 테스트 케이스: {len(test_dataset)}개")
    print(f"카테고리: {set(t['category'] for t in test_dataset)}")
    print()
    
    # 각 테스트 실행
    for i, test_case in enumerate(test_dataset, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(test_dataset)}] {test_case['id']}: {test_case['question'][:50]}...")
        print(f"{'='*80}")
        
        try:
            # Agent 호출
            response = agent.chat(test_case['question'])
            
            # 검색 문서 추출 (citations에서)
            retrieved_docs = []
            if 'citations' in response:
                for citation in response['citations']:
                    retrieved_docs.append({
                        'collection': citation.get('collection', ''),
                        'title': citation.get('title', ''),
                        'score': citation.get('score', 0),
                        'text': ''  # 전체 텍스트는 없지만 평가 가능
                    })
            
            # 평가
            result = evaluator.evaluate_single(
                test_case=test_case,
                agent_response=response,
                retrieved_docs=retrieved_docs
            )
            
        except Exception as e:
            print(f"❌ 오류: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    # 리포트 생성
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{version_name}_{timestamp}.json"
    
    filepath = evaluator.save_report(filename)
    
    # 요약 출력
    report = evaluator.generate_report()
    
    print("\n" + "="*80)
    print("📊 평가 완료 - 결과 요약")
    print("="*80)
    
    overall = report['overall_metrics']
    print(f"\n전체 평균:")
    print(f"  - Correctness: {overall['correctness']:.3f}")
    print(f"  - Faithfulness: {overall['faithfulness']:.3f}")
    print(f"  - Relevancy: {overall['relevancy']:.3f}")
    print(f"  - Similarity: {overall['similarity']:.3f}")
    print(f"  - Keyword Coverage: {overall['keyword_coverage']:.3f}")
    
    print(f"\n카테고리별:")
    for cat, metrics in report['by_category'].items():
        print(f"  {cat}:")
        print(f"    - Count: {metrics['count']}")
        print(f"    - Correctness: {metrics['correctness']:.3f}")
        print(f"    - Faithfulness: {metrics['faithfulness']:.3f}")
    
    print(f"\n💾 상세 결과: {filepath}")
    
    return report


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='FDA RAG 시스템 평가')
    parser.add_argument(
        '--version',
        type=str,
        default='baseline',
        help='버전 이름 (예: baseline, with_reranking)'
    )
    
    args = parser.parse_args()
    
    run_evaluation(args.version)