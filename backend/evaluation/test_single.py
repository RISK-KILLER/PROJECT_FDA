# evaluation/test_single.py
"""
단일 테스트 케이스 실행 스크립트
"""

import sys
import io
sys.path.append('..')

# Windows CMD에서 UTF-8 출력 지원
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from evaluation.test_dataset import get_dataset
from evaluation.evaluator import FDAEvaluator
from utils.agent import FDAAgent


def test_single_case(test_id: str = "definition_001"):
    """단일 테스트 케이스 실행"""
    
    print("="*80)
    print(f"[TEST] {test_id}")
    print("="*80)
    
    # Agent 및 Evaluator 초기화
    agent = FDAAgent()
    evaluator = FDAEvaluator()
    
    # 테스트 케이스 찾기
    test_dataset = get_dataset()
    test_case = next((t for t in test_dataset if t['id'] == test_id), None)
    
    if not test_case:
        print(f"[ERROR] 테스트 케이스를 찾을 수 없습니다: {test_id}")
        return
    
    print(f"\n[Q] 질문: {test_case['question']}")
    print(f"[A] 정답: {test_case['ground_truth'][:100]}...")
    print(f"[K] 키워드: {test_case['expected_keywords']}")
    print()
    
    try:
        # Agent 호출
        print("[Agent] 답변 생성 중...")
        response = agent.chat(test_case['question'])
        
        print(f"\n[Response] Agent 답변:")
        print("-" * 80)
        print(response.get('content', '')[:500])
        print("-" * 80)
        
        # 검색 문서 추출
        retrieved_docs = []
        if 'citations' in response:
            print(f"\n[Debug] 검색된 문서 내용:")
            for i, citation in enumerate(response['citations'], 1):
                content = citation.get('content', '')
                print(f"\n  [{i}] {citation.get('title', '')[:100]}")
                print(f"      내용 미리보기: {content[:200]}...")
                
                retrieved_docs.append({
                    'collection': citation.get('collection', ''),
                    'title': citation.get('title', ''),
                    'score': citation.get('score', 0),
                    'text': content
                })
        
        # 평가
        print("\n[Evaluation] 평가 시작...")
        result = evaluator.evaluate_single(
            test_case=test_case,
            agent_response=response,
            retrieved_docs=retrieved_docs
        )
        
        # 상세 결과 출력
        print("\n" + "="*80)
        print("[RESULT] 평가 완료")
        print("="*80)
        
        gen = result['generation']
        print(f"\n[Generation] 평가:")
        print(f"  - Correctness:       {gen['correctness']:.3f} / 1.0")
        print(f"  - Faithfulness:      {gen['faithfulness']:.3f} / 1.0")
        print(f"  - Relevancy:         {gen['relevancy']:.3f} / 1.0")
        print(f"  - Similarity:        {gen['similarity']:.3f} / 1.0")
        print(f"  - Keyword Coverage:  {gen['keyword_coverage']:.1%} ({int(gen['keyword_coverage'] * len(test_case['expected_keywords']))}/{len(test_case['expected_keywords'])})")
        
        if result['retrieval']:
            ret = result['retrieval']
            print(f"\n[Retrieval] 평가:")
            print(f"  - 검색 문서:          {ret['total_docs']}개")
            print(f"  - Keyword Coverage:  {ret['keyword_coverage']:.1%}")
            print(f"  - Avg Score:         {ret['avg_score']:.3f}")
        
        print("\n" + "="*80)
        
        return result
        
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='단일 테스트 케이스 실행')
    parser.add_argument(
        '--id',
        type=str,
        default='definition_001',
        help='테스트 케이스 ID (예: definition_001, authority_001)'
    )
    
    args = parser.parse_args()
    
    test_single_case(args.id)

