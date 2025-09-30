# development/git-workflow.md

## 브랜치 전략
```markdown
# Git Workflow Guide

## 브랜치 구조
- `main`: 프로덕션 배포 브랜치
- `develop`: 개발 통합 브랜치  
- `feature/기능명`: 새 기능 개발

## 예시
feature/tab-certificates
feature/agent-improvement
```

## 커밋 메시지 규칙
```markdown
## 커밋 메시지 형식
- feat: 새 기능 추가
- fix: 버그 수정
- refactor: 코드 리팩토링
- docs: 문서 변경
- style: 코드 스타일 변경

## 예시
feat: add certificate analysis tab
fix: resolve project deletion bug
refactor: split App.js into components
```

## 개발 프로세스
```markdown
## 기능 개발 과정
1. feature 브랜치 생성
2. 로컬에서 개발 및 테스트
3. 커밋 및 푸시
4. 필요시 main에 머지
```

## 파일 관리 규칙
```markdown
## .gitignore 관리
- node_modules/
- .env 파일들
- __pycache__/

## 대용량 파일 처리
- Git LFS 사용 고려
- 임베딩 파일은 별도 관리
```
