## deployment/environment-variables.md

```markdown
# Environment Variables Guide

## 필수 환경변수

### Backend (.env)
```bash
# OpenAI API
OPENAI_API_KEY=your_openai_api_key_here

# Qdrant Cloud
QDRANT_URL=https://your-cluster.cloud.qdrant.io:6333
QDRANT_API_KEY=your_qdrant_api_key_here

# 선택사항
ENVIRONMENT=development
LOG_LEVEL=INFO
```

### Frontend (.env)
```bash
# API 엔드포인트
REACT_APP_API_URL=http://localhost:8000

# 프로덕션 환경에서는
REACT_APP_API_URL=https://your-backend-domain.com
```

## 환경별 설정

### 개발 환경
- Backend: http://localhost:8000
- Frontend: http://localhost:3000
- Qdrant: Cloud 인스턴스

### 프로덕션 환경
- Backend: Docker 컨테이너
- Frontend: Docker 컨테이너
- 환경변수: Docker Compose로 주입

## 보안 주의사항
- .env 파일은 절대 Git에 커밋하지 않음
- API 키는 팀원과 안전한 채널로 공유
- 프로덕션에서는 환경변수를 컨테이너 런타임에 주입
```
