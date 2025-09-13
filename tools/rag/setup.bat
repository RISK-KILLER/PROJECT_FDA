@echo off
cd /d "%~dp0"
chcp 65001 > nul
echo ===============================================
echo RAG 환경 설정 시작
echo ===============================================
echo.
echo 현재 작업 디렉토리: %CD%

REM Python 버전 확인
echo Python 버전 확인 중...
python --version 2>nul
if errorlevel 1 (
    echo Python이 설치되지 않았거나 PATH에 없습니다.
    pause
    exit /b 1
)

REM 기존 가상환경 삭제
if exist "rag_venv" (
    echo 기존 RAG 가상환경 삭제 중...
    rmdir /s /q rag_venv
)

echo.
echo RAG 전용 가상환경 생성 중...
python -m venv rag_venv
if errorlevel 1 (
    echo 가상환경 생성 실패
    pause
    exit /b 1
)

echo.
echo 가상환경 활성화 중...
call rag_venv\Scripts\activate.bat

echo pip 업그레이드 중...
python -m pip install --upgrade pip

echo.
echo RAG 전용 패키지 설치 중...
pip install llama-index-core==0.11.11
pip install llama-index-embeddings-huggingface
pip install llama-index-vector-stores-chroma
pip install chromadb>=0.4.0
pip install sentence-transformers>=2.2.0
pip install torch>=2.0.0
pip install transformers>=4.21.0

echo.
echo RAG 의존성 저장 중...
pip freeze > rag_requirements.txt

REM docs 폴더 존재 확인
if not exist "..\..\docs" (
    echo docs 폴더가 없습니다. main 브랜치에서 git pull을 실행하세요.
    pause
    exit /b 1
)

echo.
echo RAG 시스템 초기화 중...
python rag.py status

echo.
echo 문서 임베딩 시작...
python rag.py update --all

echo.
echo 테스트 실행 중...
python rag.py search "프로젝트 구조"

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
echo - frontend/: React.js with tab-based UI  
echo - docs/: Project documentation ^(embedded in ChromaDB^)
echo - rag.py: ChromaDB RAG system for documentation
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
) > ..\..\.cursorrules

if exist "..\..\.cursorrules" (
    echo .cursorrules 파일이 성공적으로 생성되었습니다.
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
echo 사용법: start_work.bat 실행하여 작업 시작
echo.

deactivate
echo.
echo 설정이 완료되었습니다.
pause