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

# ⭐ 평가용 설정
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()


def test_single_case(test_id: str = "definition_001", deterministic: bool = True):
    """단일 테스트 케이스 실행
    
    Args:
        test_id: 테스트 케이스 ID
        deterministic: True이면 temperature=0으로 설정하여 일관된 결과 보장
    """
    
    print("="*80)
    print(f"[TEST] {test_id}")
    print("="*80)
    
    # ⭐ 평가용으로 temperature를 0으로 설정 (일관된 결과를 위해)
    if deterministic:
        print("🔧 평가 모드: temperature=0 (일관된 결과 보장)")
        Settings.llm = OpenAI(
            model="gpt-4-turbo", 
            temperature=0,  # ⬅️ 0으로 설정!
            api_key=os.getenv("OPENAI_API_KEY")
        )
        Settings.embed_model = OpenAIEmbedding(
            model="text-embedding-3-small", 
            api_key=os.getenv("OPENAI_API_KEY")
        )
    else:
        print("🔧 실제 챗봇 모드: temperature=0.1 (약간의 변동성)")
    
    # Agent 및 Evaluator 초기화
    agent = FDAAgent()
    evaluator = FDAEvaluator()
    
    # ⭐ 메모리 초기화 (실제 챗봇처럼 깨끗한 상태에서 시작)
    agent.reset_conversation()
    
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
            print(f"\n[Debug] 검색된 문서 상세 내용:")
            for i, citation in enumerate(response['citations'], 1):
                content = citation.get('content', '')
                print(f"\n  [{i}] {citation.get('title', '')[:100]}")
                print(f"      📏 전체 길이: {len(content)}자")
                print(f"      내용 (첫 1000자):")
                print(f"      {content[:1000]}")
                if len(content) > 1000:
                    print(f"      ... (생략: {len(content) - 1000}자)")
                
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
    parser.add_argument(
        '--real-chatbot',
        action='store_true',
        help='실제 챗봇처럼 동작 (temperature=0.1, 약간의 변동성 있음)'
    )
    
    args = parser.parse_args()
    
    # --real-chatbot 플래그가 있으면 deterministic=False
    test_single_case(args.id, deterministic=not args.real_chatbot)

