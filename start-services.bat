@echo off
REM PROJECT_FDA Windows 배포용 시작 스크립트
REM EC2에서 실행할 때 사용

echo === PROJECT_FDA 서비스 시작 ===
echo 시작 시간: %date% %time%

REM 프로젝트 디렉토리로 이동
cd /d C:\PROJECT_FDA

REM Docker 서비스 상태 확인
echo Docker 서비스 상태 확인 중...
docker --version
if %errorlevel% neq 0 (
    echo Docker가 설치되지 않았거나 실행되지 않습니다.
    exit /b 1
)

REM 기존 컨테이너 정리
echo 기존 컨테이너 정리 중...
docker-compose down 2>nul

REM 환경 변수 파일 확인
if not exist .env (
    echo 경고: .env 파일이 없습니다. 환경 변수를 확인하세요.
)

REM 서비스 시작
echo Docker Compose 서비스 시작 중...
docker-compose up -d --build

REM 서비스 상태 확인
echo 서비스 상태 확인 중...
timeout /t 10 /nobreak >nul

REM 컨테이너 상태 출력
echo === 컨테이너 상태 ===
docker-compose ps

REM 헬스체크
echo === 헬스체크 ===
for /l %%i in (1,1,5) do (
    echo 헬스체크 시도 %%i/5
    docker-compose ps | findstr "Up" >nul
    if %errorlevel% equ 0 (
        echo 서비스가 정상적으로 시작되었습니다.
        goto :success
    ) else (
        echo 서비스 시작 대기 중... (10초 후 재시도)
        timeout /t 10 /nobreak >nul
    )
)

:success
REM 최종 상태 출력
echo === 최종 서비스 상태 ===
docker-compose ps

echo === 서비스 시작 완료 ===
echo 완료 시간: %date% %time%
echo Frontend: http://localhost:3001
echo Backend: http://localhost:8002

pause
