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

# ⭐ 평가용 설정
import os
from dotenv import load_dotenv
from llama_index.core import Settings
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding

load_dotenv()


def run_evaluation(version_name: str = "baseline", deterministic: bool = True):
    """평가 실행
    
    Args:
        version_name: 버전 이름
        deterministic: True이면 temperature=0으로 설정하여 일관된 결과 보장
    """
    
    print("="*80)
    print(f"🧪 FDA RAG 시스템 평가 - {version_name}")
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
    
    # Agent 초기화
    agent = FDAAgent()
    evaluator = FDAEvaluator()
    
    # ⭐ 메모리 초기화
    agent.reset_conversation()
    
    # 테스트 데이터셋 로드
    test_dataset = get_dataset()
    
    print(f"\n📝 테스트 케이스: {len(test_dataset)}개")
    print(f"카테고리: {set(t['category'] for t in test_dataset)}")
    print()
    
    # 각 테스트 실행
    for i, test_case in enumerate(test_dataset, 1):
        print(f"\n{'='*80}")
        print(f"[{i}/{len(test_dataset)}] {test_case['id']}")
        print(f"{'='*80}")
        print(f"❓ 질문: {test_case['question']}")
        print(f"✅ 정답: {test_case['ground_truth'][:100]}...")
        print(f"🔑 키워드: {test_case['expected_keywords']}")
        print()
        
        try:
            # Agent 호출
            print("🤖 Agent 답변 생성 중...")
            response = agent.chat(test_case['question'])
            
            # 답변 미리보기
            content = response.get('content', '')
            print(f"\n📝 답변 (첫 200자):")
            print(f"   {content[:200]}...")
            
            # 검색 문서 추출 (citations에서)
            retrieved_docs = []
            if 'citations' in response:
                print(f"\n📚 검색된 문서: {len(response['citations'])}개")
                for j, citation in enumerate(response['citations'], 1):
                    content = citation.get('content', '')
                    print(f"   [{j}] {citation.get('collection', 'N/A')}: {citation.get('title', 'N/A')[:60]}... (점수: {citation.get('score', 0):.3f})")
                    
                    retrieved_docs.append({
                        'collection': citation.get('collection', ''),
                        'title': citation.get('title', ''),
                        'score': citation.get('score', 0),
                        'text': content  # ⭐ 실제 content 사용
                    })
            
            # 평가
            print("\n📊 평가 시작...")
            result = evaluator.evaluate_single(
                test_case=test_case,
                agent_response=response,
                retrieved_docs=retrieved_docs
            )
            
            # 간단한 결과 출력
            gen = result['generation']
            print(f"\n✅ 평가 완료:")
            print(f"   - Correctness:  {gen['correctness']:.2f}")
            print(f"   - Faithfulness: {gen['faithfulness']:.2f}")
            print(f"   - Keyword:      {gen['keyword_coverage']:.0%}")
            
        except Exception as e:
            print(f"\n❌ 오류: {e}")
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
    print("🎯 평가 완료 - 최종 결과")
    print("="*80)
    
    overall = report['overall_metrics']
    print(f"\n📊 전체 평균 점수:")
    print(f"  ✅ Correctness (정확성):     {overall['correctness']:.3f} / 1.0")
    print(f"  📝 Faithfulness (충실도):    {overall['faithfulness']:.3f} / 1.0")
    print(f"  🎯 Relevancy (관련성):       {overall['relevancy']:.3f} / 1.0")
    print(f"  🔍 Similarity (유사도):      {overall['similarity']:.3f} / 1.0")
    print(f"  🔑 Keyword Coverage (키워드): {overall['keyword_coverage']:.1%}")
    
    # 전체 평가
    avg_score = (overall['correctness'] + overall['faithfulness'] + overall['relevancy']) / 3
    if avg_score >= 0.9:
        grade = "A+ (우수)"
    elif avg_score >= 0.8:
        grade = "A (양호)"
    elif avg_score >= 0.7:
        grade = "B+ (보통)"
    else:
        grade = "B (개선 필요)"
    
    print(f"\n🏆 종합 평가: {grade}")
    
    print(f"\n📂 카테고리별 상세:")
    for cat, metrics in report['by_category'].items():
        print(f"\n  📌 {cat} ({metrics['count']}개 테스트)")
        print(f"     - Correctness:  {metrics['correctness']:.3f}")
        print(f"     - Faithfulness: {metrics['faithfulness']:.3f}")
    
    print(f"\n💾 상세 결과 저장: {filepath}")
    print(f"📁 파일 위치: backend/evaluation/results/")
    print("\n" + "="*80)
    
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
    parser.add_argument(
        '--real-chatbot',
        action='store_true',
        help='실제 챗봇처럼 동작 (temperature=0.1, 약간의 변동성 있음)'
    )
    
    args = parser.parse_args()
    
    run_evaluation(args.version, deterministic=not args.real_chatbot)