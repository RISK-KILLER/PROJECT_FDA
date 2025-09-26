#!/bin/bash

# PROJECT_FDA 자동 시작 스크립트
# EC2 재부팅 시 Docker 서비스들을 자동으로 시작합니다.

set -e

echo "=== PROJECT_FDA 서비스 시작 ==="
echo "시작 시간: $(date)"

# 프로젝트 디렉토리로 이동
cd /home/ec2-user/PROJECT_FDA || cd /home/ubuntu/PROJECT_FDA || {
    echo "프로젝트 디렉토리를 찾을 수 없습니다."
    exit 1
}

# Docker 서비스 상태 확인
echo "Docker 서비스 상태 확인 중..."
if ! systemctl is-active --quiet docker; then
    echo "Docker 서비스를 시작합니다..."
    sudo systemctl start docker
    sleep 5
fi

# Docker Compose가 실행 중인지 확인
echo "기존 컨테이너 정리 중..."
docker-compose down 2>/dev/null || true

# 환경 변수 파일 확인
if [ ! -f .env ]; then
    echo "경고: .env 파일이 없습니다. 환경 변수를 확인하세요."
fi

# 서비스 시작
echo "Docker Compose 서비스 시작 중..."
docker-compose up -d --build

# 서비스 상태 확인
echo "서비스 상태 확인 중..."
sleep 10

# 컨테이너 상태 출력
echo "=== 컨테이너 상태 ==="
docker-compose ps

# 헬스체크
echo "=== 헬스체크 ==="
for i in {1..5}; do
    echo "헬스체크 시도 $i/5"
    if docker-compose ps | grep -q "Up"; then
        echo "서비스가 정상적으로 시작되었습니다."
        break
    else
        echo "서비스 시작 대기 중... (10초 후 재시도)"
        sleep 10
    fi
done

# 최종 상태 출력
echo "=== 최종 서비스 상태 ==="
docker-compose ps

echo "=== 서비스 시작 완료 ==="
echo "완료 시간: $(date)"
echo "Frontend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):3001"
echo "Backend: http://$(curl -s http://169.254.169.254/latest/meta-data/public-ipv4):8002"
