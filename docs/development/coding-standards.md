# development/coding-standards.md

```markdown
## 명명 규칙
- 변수명: camelCase (JavaScript), snake_case (Python)
- 상수: UPPER_CASE
- 파일명: kebab-case (my-component.js)
- 함수명: 동사로 시작 (getUserData, handleClick)

## 코드 포맷팅
- 들여쓰기: JavaScript 2칸, Python 4칸
- 세미콜론: JavaScript에서 필수
- 따옴표: 일관성 유지 (double)

## 에러 처리
- try-catch 블록 사용법
- 의미있는 에러 메시지 작성
- 로깅 레벨 구분 (INFO, ERROR, DEBUG)
```

## 함수 작성 규칙
- 변경 필요한 부분만 제시
- 복잡한 로직은 단계별로 분리
- 한국어/영어 주석 병행

## 파일 구조
- utils/: 공통 유틸리티
- components/: 재사용 컴포넌트