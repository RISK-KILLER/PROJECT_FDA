## deployment/docker-setup.md

```markdown
# Docker Setup Guide

## 프로젝트 구조
```
PROJECT_FDA/
├── docker-compose.yml
├── backend/
│   ├── Dockerfile
│   └── requirements.txt
└── frontend/
    ├── Dockerfile
    └── package.json
```

## Docker Compose 실행
```bash
# 빌드 및 실행
docker-compose up --build

# 백그라운드 실행
docker-compose up -d

# 로그 확인
docker-compose logs -f backend
docker-compose logs -f frontend

# 서비스 중지
docker-compose down
```

## 개별 컨테이너 관리
```bash
# 특정 서비스만 재시작
docker-compose restart backend

# 컨테이너 접속
docker-compose exec backend bash
docker-compose exec frontend sh
```

## 트러블슈팅
- 포트 충돌: 다른 서비스가 3000/8000 포트 사용 중인지 확인
- 빌드 실패: requirements.txt, package.json 의존성 확인
- 네트워크 문제: docker network ls로 네트워크 상태 확인
```