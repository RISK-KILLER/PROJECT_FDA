# test_integration.py
from utils.agent import FDAAgent

def test_complex_queries():
    """7개 컬렉션이 협업하는 복합 질의"""

    agent = FDAAgent()

    complex_queries = [
        # 1. 전체 수출 프로세스 (5-7개 컬렉션 필요)
        "냉동 만두를 미국에 수출하려고 하는데, 필요한 규제 전체를 알려줘",

        # 2. Import Alert + FSVP 연계
        "한국산 김치가 Import Alert 받은 적 있어? 있으면 FSVP 검증은 어떻게 해야 해?",

        # 3. 재료 안전성 + 라벨링
        "대두가 들어간 식품 수출 시 GRAS 확인하고 라벨링은 어떻게 해야 해?",

        # 4. 제조 기준 + 절차
        "HACCP 적용 식품의 개인용 수입 절차는?",

        # 5. 법적 위반 + 처벌
        "부정표시로 적발되면 처벌은? Import Alert 받으면 재수출 가능해?",

        # 6. 특정 성분 전반
        "해산물 관련된 모든 FDA 규제 (GRAS, CFR, Import Alert, 라벨링) 알려줘",

        # 7. 시나리오 기반
        "새우튀김 수출인데, 수입 검사에서 거부당했어. 어떻게 해야 하고, 비용은 누가 내?"
    ]

    for i, query in enumerate(complex_queries, 1):
        print(f"\n{'='*80}")
        print(f"통합 테스트 {i}/{len(complex_queries)}")
        print(f"{'='*80}")
        print(f"질문: {query}\n")

        try:
            response = agent.chat(query)

            # 응답 분석
            print(f"답변:\n{response['content']}\n")
            print(f"사용된 출처: {response.get('sources', [])}")
            print(f"참조 CFR: {len(response.get('cfr_references', []))}개")

            agent.reset_conversation()

        except Exception as e:
            print(f"오류: {e}")

if __name__ == "__main__":
    test_complex_queries()
