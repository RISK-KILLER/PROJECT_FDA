## frontend/tab-system.md

```markdown
# Tab System Architecture

## 현재 구조
App.js에서 activeTab state로 탭 전환 관리

## 탭 종류
- `regulations`: 기본 규제 확인 (채팅 기능)
- `certificates`: 인증서 분석 (개발 예정)
- `documents`: 서류 준비 (개발 예정) 
- `checklist`: 최종 체크리스트 (개발 예정)

## 탭 추가 방법
1. progressSteps 배열에 새 탭 정보 추가
2. renderTabContent()에 case 추가
3. 해당 탭 컴포넌트 구현

## 상태 관리
- activeTab: 현재 활성 탭
- messages: regulations 탭 전용
- 각 탭별 독립된 상태 필요 시 별도 state 추가
```