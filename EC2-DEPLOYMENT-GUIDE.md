# EC2 배포 및 자동 재시작 설정 가이드

## 문제 해결 완료 사항

### 1. Docker Compose 재시작 정책 추가
- `docker-compose.yml`에 `restart: unless-stopped` 정책 추가
- 헬스체크 기능 추가로 컨테이너 상태 모니터링

### 2. Frontend 프로덕션 최적화
- 개발 모드(`npm start`) → 프로덕션 모드(nginx + 빌드된 정적 파일)
- 메모리 효율성 및 안정성 향상

### 3. Backend 헬스체크 엔드포인트 추가
- `/health` 엔드포인트로 서비스 상태 확인 가능

## EC2 배포 단계

### 1. 파일 업로드
```bash
# EC2 인스턴스에 접속 후
scp -i your-key.pem -r C:\PROJECT_FDA ec2-user@your-ec2-ip:/home/ec2-user/
```

### 2. 자동 시작 설정 (Linux)
```bash
# EC2 인스턴스에서 실행
sudo cp project-fda.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable project-fda.service
sudo systemctl start project-fda.service
```

### 3. 수동 시작 (Windows 환경에서)
```bash
# EC2에서 직접 실행
start-services.bat
```

### 4. 서비스 상태 확인
```bash
# Linux
sudo systemctl status project-fda.service
docker-compose ps

# Windows
docker-compose ps
```

## 재부팅 후 자동 시작 확인

### Linux (systemd 사용)
- EC2 재부팅 시 자동으로 Docker 서비스 시작
- `project-fda.service`가 자동으로 컨테이너들 시작

### Windows
- EC2 재부팅 후 수동으로 `start-services.bat` 실행 필요
- 또는 Windows 작업 스케줄러에 등록 가능

## 트러블슈팅

### 컨테이너가 시작되지 않는 경우
```bash
# 로그 확인
docker-compose logs frontend
docker-compose logs backend

# 컨테이너 재시작
docker-compose restart frontend
docker-compose restart backend
```

### 포트 충돌 확인
```bash
# 포트 사용 확인
netstat -tulpn | grep :3001
netstat -tulpn | grep :8002
```

### 환경 변수 확인
```bash
# .env 파일 존재 확인
ls -la .env
cat .env
```

## 모니터링 명령어

```bash
# 실시간 로그 확인
docker-compose logs -f

# 컨테이너 상태 확인
docker-compose ps

# 리소스 사용량 확인
docker stats

# 헬스체크 확인
curl http://localhost:8002/health
curl http://localhost:3001
```

## 주요 개선사항

1. **안정성**: 프로덕션용 nginx 서버 사용
2. **자동 복구**: `restart: unless-stopped` 정책
3. **모니터링**: 헬스체크 기능 추가
4. **자동 시작**: systemd 서비스 등록
5. **로그 관리**: 구조화된 로그 출력

이제 EC2 재부팅 후에도 frontend 서버가 자동으로 시작되고 안정적으로 동작할 것입니다.
