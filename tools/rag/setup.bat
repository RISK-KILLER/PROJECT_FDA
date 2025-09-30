@echo off
setlocal
cd /d "%~dp0"
chcp 65001 > nul

echo ===============================================
echo RAG 환경 설정 시작
echo ===============================================
echo.
echo 현재 작업 디렉토리: %CD%

REM Git 브랜치 정보 가져오기
for /f "delims=" %%i in ('git branch --show-current 2^>nul') do set BRANCH_NAME=%%i
if not defined BRANCH_NAME set BRANCH_NAME=main
echo 현재 브랜치: %BRANCH_NAME%

REM Python 버전 확인
echo.
echo Python 버전 확인 중...
call python --version 2>nul
if errorlevel 1 (
    echo Python이 설치되지 않았거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 기존 가상환경 삭제
if exist "rag_venv" (
    echo.
    echo 기존 RAG 가상환경 삭제 중...
    rmdir /s /q rag_venv
    echo 삭제 완료
)

echo.
echo RAG 전용 가상환경 생성 중...
call python -m venv rag_venv
if errorlevel 1 (
    echo 가상환경 생성 실패
    pause
    exit /b 1
)

if not exist "rag_venv\Scripts\activate.bat" (
    echo 가상환경 생성 실패: activate.bat 파일이 없습니다
    pause
    exit /b 1
)
echo 가상환경 생성 완료

echo.
echo 가상환경 활성화 중...
call rag_venv\Scripts\activate.bat
echo 가상환경 활성화 완료

echo.
echo pip 업그레이드 중...
call python -m pip install --upgrade pip

echo.
echo ===============================================
echo RAG 전용 패키지 설치 중...
echo ===============================================
echo.

echo [1/7] llama-index-core 설치 중...
call pip install llama-index-core==0.11.11

echo.
echo [2/7] llama-index-embeddings-huggingface 설치 중...
call pip install llama-index-embeddings-huggingface

echo.
echo [3/7] llama-index-vector-stores-chroma 설치 중...
call pip install llama-index-vector-stores-chroma

echo.
echo [4/7] chromadb 설치 중...
call pip install "chromadb>=0.4.0"

echo.
echo [5/7] sentence-transformers 설치 중...
call pip install "sentence-transformers>=2.2.0"

echo.
echo [6/7] torch 설치 중 (시간이 오래 걸릴 수 있습니다)...
call pip install "torch>=2.0.0"

echo.
echo [7/7] transformers 설치 중...
call pip install "transformers>=4.21.0"

echo.
echo RAG 의존성 저장 중...
call pip freeze > rag_requirements.txt
echo 의존성 파일 생성 완료: rag_requirements.txt

REM docs 폴더 존재 확인
echo.
echo docs 폴더 확인 중...
if not exist "..\..\docs" (
    echo WARNING: docs 폴더가 없습니다.
    echo 경로: %CD%\..\..\docs
    echo main 브랜치에서 git pull을 실행하거나 docs 폴더를 생성하세요.
    REM 일단 계속 진행
) else (
    echo docs 폴더 확인 완료
)

REM rag.py 파일 존재 확인
if not exist "rag.py" (
    echo ERROR: rag.py 파일이 없습니다!
    echo 현재 경로: %CD%
    pause
    exit /b 1
)

echo.
echo ===============================================
echo RAG 시스템 초기화 중...
echo ===============================================
call python rag.py status

REM docs 폴더가 있을 때만 임베딩 수행
if exist "..\..\docs" (
    echo.
    echo ===============================================
    echo 문서 임베딩 시작...
    echo ===============================================
    call python rag.py update --all
    
    echo.
    echo ===============================================
    echo 테스트 검색 실행 중...
    echo ===============================================
    call python rag.py search "프로젝트 구조"
) else (
    echo.
    echo docs 폴더가 없어 임베딩을 건너뜁니다.
    echo 나중에 'python rag.py update --all' 명령으로 수동 임베딩하세요.
)

echo.
echo ===============================================
echo Cursor AI 규칙 파일 생성 중...
echo ===============================================

REM .cursorrules 파일 생성
echo 프로젝트 루트에 .cursorrules 파일 생성 중...
(
echo # Cursor AI Rules for PROJECT_FDA
echo.
echo ## Project Context
echo This is a React + FastAPI FDA export regulation assistant using ReAct Agent.
echo Current branch: %BRANCH_NAME%
echo.
echo ## RAG Usage Rules - MANDATORY
echo ALWAYS use RAG search before answering project-related questions:
echo   python rag.py search "your query"
echo.
echo ## File Structure
echo - backend/: FastAPI server with ReAct Agent
echo - frontend: React.js with tab-based UI  
echo - docs/: Project documentation ^(embedded in ChromaDB^)
echo - tools/rag/: ChromaDB RAG system for documentation
echo.
echo ## Coding Guidelines
echo Follow patterns documented in ChromaDB. Use RAG search for context.
echo Check docs/ folder structure for reference, but use RAG for content.
echo.
echo ## Key Technologies
echo - Backend: FastAPI, LlamaIndex, ReAct Agent, Qdrant Cloud
echo - Frontend: React, Tailwind CSS, Lucide React  
echo - RAG: ChromaDB, sentence-transformers
echo - Database: Qdrant Vector Database
echo.
echo ## Development Workflow
echo 1. Always check RAG before making changes: python rag.py search "topic"
echo 2. Follow existing patterns found in RAG search results
echo 3. Update documentation when adding new features
echo 4. Use RAG to understand project architecture
) > ..\..\.cursorrules

if exist "..\..\.cursorrules" (
    echo .cursorrules 파일이 성공적으로 생성되었습니다.
    echo 경로: %CD%\..\..\cursorrules
) else (
    echo .cursorrules 파일 생성에 실패했습니다.
)

echo.
echo ===============================================
echo 설치 완료!
echo ===============================================
echo.
echo RAG 시스템 사용 규칙:
echo - 모든 프로젝트 관련 질문에 대해 RAG 검색 필수
echo - 파일 직접 읽기 대신 RAG 검색 사용
echo - docs 폴더는 참조용으로 유지, 내용은 RAG 검색으로 확인
echo.
echo 다음 단계:
echo 1. start_work.bat 실행하여 작업 시작
echo 2. Cursor AI에서 프로젝트 루트 폴더 열기
echo 3. 모든 질문 전에 RAG 검색 사용
echo.

call deactivate
echo.
echo 설정이 완료되었습니다. 창을 닫으셔도 됩니다.
pause
endlocal