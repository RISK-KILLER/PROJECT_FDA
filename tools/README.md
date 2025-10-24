# Project Development Tools

이 폴더는 PROJECT_FDA 개발을 지원하는 도구들을 포함합니다.

## RAG 문서 검색 시스템

### 개요
프로젝트 문서(docs/ 폴더)를 ChromaDB에 임베딩하여 Cursor AI가 정확한 컨텍스트를 제공받을 수 있도록 하는 RAG 시스템입니다.

### 필수 요구사항
- Python 3.8 이상
- Git (브랜치 정보 확인용)

### 설치 및 사용법

#### 1. 초기 설정
```bash
cd tools/
setup.bat
```

#### 2. 작업 시작
```bash
start_work.bat
```

#### 3. RAG 검색 사용
```bash
python rag.py search "검색할 내용"
python rag.py status
python rag.py update --all
```

### 브랜치별 독립 ChromaDB
각 Git 브랜치마다 독립적인 ChromaDB 컬렉션을 생성하여 브랜치별 개발 컨텍스트를 제공합니다.

```
main → project_docs_main
feature/certificates → project_docs_feature_certificates
```

### Cursor AI 통합
- `.cursorrules` 파일을 자동 생성하여 Cursor AI가 RAG 시스템 사용을 강제합니다
- 모든 프로젝트 관련 질문에 대해 RAG 검색 필수

### 파일 구조
```
tools/
├── rag.py              # RAG 시스템 메인 스크립트
├── setup.bat           # 초기 환경 설정
├── start_work.bat      # 작업 환경 시작
├── rag_venv/           # RAG 전용 가상환경 (자동 생성)
├── chroma_db/          # ChromaDB 로컬 저장소 (자동 생성)
└── README.md           # 이 파일
```

### 주의사항
- 이 도구는 개발자 로컬 환경에서만 사용됩니다
- 프로덕션 배포에는 포함되지 않습니다
- docs/ 폴더의 원본 파일은 수정하지 마세요 (GitIgnore 대상 아님)

### 문제 해결
- 가상환경 오류: `setup.bat` 재실행
- ChromaDB 오류: `python rag.py delete --confirm` 후 `python rag.py update --all`
- 브랜치 변경 후: `python rag.py update --all`로 문서 업데이트