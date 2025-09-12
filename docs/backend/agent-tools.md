## backend/agent-tools.md

```markdown
# Agent Tools

## 사용 가능한 도구 (11개)
ReAct Agent가 상황에 따라 자동으로 선택하는 전문가 도구들

### Guidance 도구 (FDA 지침)
- `guidance_allergen`: 알레르기 지침
- `guidance_labeling`: 라벨링 지침  
- `guidance_additives`: 첨가물 지침
- `guidance_cpg`: 규정 준수 정책 가이드

### Regulation 도구 (법적 규정)
- `regulation_allergen`: 알레르기 법규
- `regulation_labeling`: 라벨링 법규
- `regulation_additives`: 첨가물 법규
- `regulation_standards`: 식품 표준 규정
- `regulation_manufacturing`: 제조 공정 규정
- `regulation_general`: 일반 FDA 법규
- `regulation_usc`: 미국 연방 법전

## 도구 선택 로직
Agent가 질문을 분석하여 가장 적절한 도구(들)을 자동으로 선택
예: "라벨링 규제" → `regulation_labeling` 선택
```