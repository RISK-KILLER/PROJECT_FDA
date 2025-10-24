# ReAct Agent Flow

## Think → Act → Observe 사이클
ReAct (Reasoning + Acting) 프레임워크는 LLM이 추론과 행동을 반복하면서 문제를 해결합니다.

### 1. Think (사고)
- 사용자 질문 분석
- 어떤 정보가 필요한지 판단
- 검색 전략 수립

### 2. Act (행동)
- 적절한 FDA 문서 컬렉션 선택
- 검색 쿼리 생성 (한국어 → 영어 변환)
- 벡터 검색 실행

### 3. Observe (관찰)
- 검색 결과 분석
- 정보가 충분한지 판단
- 추가 검색 필요 여부 결정

## 실제 동작 예시

### 예시 1: 단일 컬렉션 검색
```
Input: "대두가 GRAS 승인되었나요?"

Think: GRAS 데이터베이스에서 대두(soy/soybean) 승인 상태 확인 필요
Act: GRAS 컬렉션에서 "soy soybean approved" 검색
Observe: 충분한 정보 획득
Answer: GRAS 승인 상태 및 GRN 번호 제공
```

### 예시 2: 정보 부족 시 한계 인정
```
Input: "냉동김밥 수출 규제"

Think: 라벨링 + 수출 규정 확인 필요
Act: Guidance 컬렉션에서 "frozen food labeling export" 검색
Observe: 일반적인 라벨링 정보만 있음, 김밥 특화 정보 부족
Think: 추가 검색 필요
Act: ECFR 컬렉션에서 "frozen food manufacturing" 검색
Observe: 제조 기준만 있음, 김밥 수출 특화 정보 없음
Answer: "FDA 문서에는 김밥 특화 규정이 없습니다. 일반 냉동식품 기준을 따르며, 자세한 사항은 FDA에 직접 문의하세요."
```

### 예시 3: 다중 컬렉션 활용
```
Input: "중국산 해산물 수입 시 주의사항"

Think: Import Alert + 일반 수입 규정 확인 필요
Act: DWPE 컬렉션에서 "China seafood import alert detention" 검색
Observe: Import Alert 정보 획득
Think: 수입자 검증 절차도 확인 필요
Act: FSVP 컬렉션에서 "foreign supplier verification seafood" 검색
Observe: FSVP 요구사항 획득
Answer: Import Alert 상태 + FSVP 의무사항 종합 제공
```

## 컬렉션 선택 로직

### 자동 선택 기준
- **키워드 매칭**: 질문 내 키워드로 컬렉션 자동 선택
- **컨텍스트 이해**: 질문의 의도 파악 (승인 조회 vs 법규 확인 vs 수입 경고)
- **영어 변환**: 한국어 키워드를 영어 동의어로 확장하여 검색

### 검색 최적화
- **similarity_top_k=5**: 각 컬렉션에서 상위 5개 결과
- **영어 쿼리 필수**: 모든 FDA 문서는 영어로 작성됨
- **동의어 확장**: "해산물" → "fish fishery seafood shellfish aquatic marine"

## 한계 인정 철학
- **정보가 없으면 솔직하게 인정**: "FDA 문서에는 해당 정보가 없습니다"
- **대안 제시**: "FDA에 직접 문의하세요", "일반 기준을 따르세요"
- **과도한 추론 금지**: 없는 정보를 만들어내지 않음

## 구현 위치
- **agent.py**: ReAct Agent 메인 로직
- **tools.py**: 6개 컬렉션별 검색 도구
- **orchestrator.py**: Agent 실행 오케스트레이션
- **memory.py**: 대화 기록 관리 (Think-Act-Observe 히스토리)