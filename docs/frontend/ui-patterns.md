## frontend/ui-patterns.md

```markdown
# UI Patterns Guide

## 색상 시스템
- Primary: indigo-600 to purple-600 (그라데이션)
- Success: green-500
- Warning: amber-500  
- Gray: gray-400~900 (텍스트, 배경)

## 버튼 패턴
```jsx
// Primary 버튼
className="bg-gradient-to-r from-indigo-600 to-purple-600 text-white px-6 py-3 rounded-xl"

// Secondary 버튼  
className="bg-indigo-100 text-indigo-700 px-3 py-2 rounded-lg"
```

## 레이아웃 구조
- Sidebar: 320px 고정폭
- Main: flex-1 (나머지 공간)
- 반응형: 모바일에서는 사이드바 숨김 고려

## 아이콘 사용법
- lucide-react 라이브러리 사용
- 일관된 크기: w-4 h-4 (버튼 내), w-5 h-5 (아이콘 단독)
```