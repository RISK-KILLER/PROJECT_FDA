@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
chcp 65001 > nul

echo ===============================================
echo RAG 작업 환경 시작
echo ===============================================
echo.
echo 현재 디렉토리: %CD%

REM Git 브랜치 정보 가져오기
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set CURRENT_BRANCH=%%i
if not defined CURRENT_BRANCH set CURRENT_BRANCH=unknown

echo 현재 Git 브랜치: %CURRENT_BRANCH%
echo.

REM 가상환경 존재 확인
if not exist "rag_venv\Scripts\activate" (
    echo RAG 가상환경이 없습니다. setup.bat를 먼저 실행하세요.
    pause
    exit /b 1
)

echo 가상환경 활성화 중...
call rag_venv\Scripts\activate

echo.
echo ===============================================
echo RAG 시스템 상태 확인
echo ===============================================
python rag.py status
echo.

echo ===============================================
echo RAG 시스템 사용 가이드
echo ===============================================
echo.
echo 필수 규칙: 모든 프로젝트 관련 질문은 RAG 검색 사용!
echo.
echo 자주 사용하는 RAG 검색 명령어:
echo.
echo 📋 기본 명령어:
echo   python rag.py status                    # 컬렉션 상태 확인
echo   python rag.py update --all              # 문서 전체 업데이트
echo   python rag.py search "질문"             # 문서 검색
echo.
echo 📋 일반적인 검색 예시:
echo   python rag.py search "프로젝트 구조"
echo   python rag.py search "코딩 컨벤션"  
echo   python rag.py search "Git 워크플로우"
echo   python rag.py search "API 엔드포인트"
echo   python rag.py search "컴포넌트 구조"
echo   python rag.py search "배포 방법"
echo.
echo 📋 기술 관련 검색:
echo   python rag.py search "ReAct Agent"
echo   python rag.py search "탭 시스템"
echo   python rag.py search "환경 변수"
echo   python rag.py search "Docker 설정"
echo.
echo ⛔ 금지 사항:
echo   - 파일 직접 읽기 금지 (README.md, package.json 등)
echo   - RAG 검색 없이 추측 답변 금지
echo   - docs 폴더 파일 직접 참조 금지
echo.
echo ===============================================
echo 브랜치별 ChromaDB 확인
echo ===============================================
echo 현재 브랜치: %CURRENT_BRANCH%
echo ChromaDB 컬렉션: project_docs_%CURRENT_BRANCH%
echo.
echo 브랜치가 변경된 경우 다음 명령으로 문서 업데이트:
echo   python rag.py update --all
echo.
echo ===============================================
echo 작업 환경 준비 완료
echo ===============================================
echo.
echo Cursor AI가 .cursorrules를 자동으로 인식합니다.
echo 모든 질문에 대해 RAG 검색을 사용하세요!
echo.
echo 작업 완료 후 'deactivate' 명령으로 가상환경을 종료하세요.
echo.

REM 명령 프롬프트를 열린 상태로 유지
cmd /k