# test_allergen_coverage.py
import json
from utils.agent import FDAAgent

# 테스트 케이스 (알레르기 제품 10개)
test_cases = [
    {"product": "새우튀김", "allergens": ["shellfish", "wheat"]},
    {"product": "땅콩버터", "allergens": ["peanuts"]},
    {"product": "우유", "allergens": ["milk"]},
    {"product": "김밥", "allergens": ["fish", "sesame", "soybeans"]},
    {"product": "아몬드초콜릿", "allergens": ["tree nuts", "milk"]},
    {"product": "계란말이", "allergens": ["eggs"]},
    {"product": "연어", "allergens": ["fish"]},
    {"product": "두부", "allergens": ["soybeans"]},
    {"product": "참깨과자", "allergens": ["sesame", "wheat"]},
    {"product": "치즈", "allergens": ["milk"]},
]

def test_allergen_mentions(agent, test_cases):
    results = []
    
    for case in test_cases:
        query = f"{case['product']}을 수출하려고 하는데 어떤 규제 확인해야 하나요?"
        
        # 응답 생성
        response = agent.chat(query)
        content = response['content'].lower()
        
        # 알레르기 키워드 체크
        allergen_keywords = ['알레르기', 'allergen', '알러지', '유발']
        has_allergen_mention = any(kw in content for kw in allergen_keywords)
        
        # 구체적 알레르기 성분 언급 체크
        mentioned_allergens = []
        allergen_map = {
            "shellfish": ["갑각류", "조개", "새우", "shellfish"],
            "wheat": ["밀", "wheat", "글루텐"],
            "peanuts": ["땅콩", "peanut"],
            "milk": ["우유", "유제품", "milk", "dairy"],
            "fish": ["생선", "어류", "fish"],
            "sesame": ["참깨", "sesame"],
            "soybeans": ["대두", "콩", "soy"],
            "eggs": ["계란", "난류", "egg"],
            "tree nuts": ["견과류", "아몬드", "호두", "nut"],
        }
        
        for allergen in case['allergens']:
            keywords = allergen_map.get(allergen, [])
            if any(kw in content for kw in keywords):
                mentioned_allergens.append(allergen)
        
        # 결과 저장
        result = {
            "product": case['product'],
            "expected_allergens": case['allergens'],
            "has_allergen_mention": has_allergen_mention,
            "mentioned_allergens": mentioned_allergens,
            "coverage_rate": len(mentioned_allergens) / len(case['allergens']) * 100,
            "response_snippet": content[:200]
        }
        results.append(result)
        
        print(f"\n{'='*60}")
        print(f"제품: {case['product']}")
        print(f"기대 알레르기: {case['allergens']}")
        print(f"알레르기 언급 여부: {has_allergen_mention}")
        print(f"언급된 알레르기: {mentioned_allergens}")
        print(f"커버리지: {result['coverage_rate']:.1f}%")
        print(f"{'='*60}")
    
    # 전체 통계
    total_coverage = sum(r['coverage_rate'] for r in results) / len(results)
    mention_rate = sum(1 for r in results if r['has_allergen_mention']) / len(results) * 100
    
    print(f"\n\n📊 전체 통계:")
    print(f"알레르기 언급률: {mention_rate:.1f}% ({sum(1 for r in results if r['has_allergen_mention'])}/{len(results)})")
    print(f"평균 커버리지: {total_coverage:.1f}%")
    
    # JSON 저장
    with open('allergen_test_results.json', 'w', encoding='utf-8') as f:
        json.dump({
            "results": results,
            "summary": {
                "mention_rate": mention_rate,
                "average_coverage": total_coverage
            }
        }, f, ensure_ascii=False, indent=2)
    
    return results

# 실행
if __name__ == "__main__":
    # 방안 1 테스트: 알레르기 체크 비활성화
    agent = FDAAgent()
    
    print("🔬 알레르기 체크 로직 완화 실험 시작...")
    print("방안 1: guidance 필수 조건 제거\n")
    
    results = test_allergen_mentions(agent, test_cases)