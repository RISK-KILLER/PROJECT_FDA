# Agent Tools

## 사용 가능한 FDA 문서 컬렉션 (6개)
ReAct Agent가 상황에 따라 자동으로 선택하는 FDA 문서 컬렉션들

### 1. GRAS (Generally Recognized As Safe)
- **용도**: 식품 첨가물 안전성 및 승인 상태 조회
- **키워드**: GRN, GRAS, 물질, 첨가물, substance, approved, withdrawn
- **예시**: "대두가 GRAS 승인되었나요?"

### 2. ECFR (21 CFR - Code of Federal Regulations)
- **용도**: 제조 기준, CGMP, 식품 안전 규정
- **키워드**: CFR, 21 CFR, 규정, 제조, HACCP, regulation
- **예시**: "21 CFR 117 HACCP 요구사항"

### 3. DWPE (Import Alert & Detention)
- **용도**: 수입 거부 정보, 국가별 위반 사례, 자동 억류
- **키워드**: Import Alert, Red List, 수입 거부, detention
- **예시**: "중국산 해산물 수입 경고"

### 4. FSVP (Foreign Supplier Verification Program)
- **용도**: 수입자 책임, 공급업체 검증 절차
- **키워드**: FSVP, 수입자, 검증, supplier verification, importer
- **예시**: "FSVP 수입자 의무사항"

### 5. Guidance (FDA 지침 문서 및 CPG)
- **용도**: 정책 해석, 준수 권장사항, 라벨링 요구사항
- **키워드**: Guidance, CPG, 가이드, 라벨링, labeling, allergen
- **예시**: "알레르기 표시 가이드라인"

### 6. USC (21 USC - United States Code)
- **용도**: 법적 정의, 금지 행위, 처벌 규정
- **키워드**: 21 USC, U.S.C, 법률, 처벌, penalties, misbranding
- **예시**: "부정표시 처벌 규정"

## 컬렉션 선택 로직
- Agent가 질문을 분석하여 가장 적절한 컬렉션을 자동으로 선택
- 영어로 검색: 한국어 키워드는 자동으로 영어로 변환
- similarity_top_k=5: 각 컬렉션에서 상위 5개 문서 검색
- 모델: gpt-4o-mini 사용