# PROJECT_FDA

RAG(Retrieval-Augmented Generation) 시스템을 활용한 FDA 수출 지원 서비스

## 📋 프로젝트 개요

이 프로젝트는 RAG 기술을 활용하여 FDA 관련 정보를 효율적으로 검색하고 제공하는 시스템입니다. Python FastAPI 백엔드와 React 프론트엔드로 구성되어 있으며, Qdrant 벡터 데이터베이스를 통해 의미 기반 검색을 지원합니다.

## 🏗️ 시스템 아키텍처

```
PROJECT_FDA/
├── backend/                 # Python FastAPI 서버
│   ├── main.py             # 메인 서버 파일
│   ├── rag_engine.py       # RAG 시스템 핵심 엔진
│   ├── keyword_mapper.py   # 키워드 매핑 처리
│   ├── qdrant_client.py    # Qdrant 벡터 DB 클라이언트
│   ├── product_keyword_mappings.json  # 제품-키워드 매핑 데이터
│   ├── requirements.txt    # Python 의존성
│   └── Dockerfile          # 컨테이너 설정
├── frontend/               # React 웹 애플리케이션
│   ├── src/
│   │   ├── App.js         # 메인 React 컴포넌트
│   │   ├── App.css        # 스타일링
│   │   └── index.js       # React 앱 진입점
│   └── public/
│       └── index.html     # HTML 템플릿
├── docs/                  # 프로젝트 문서
├── .github/              # GitHub Actions 워크플로우
└── docker-compose.yml    # 다중 컨테이너 설정
```

## 🚀 주요 기능

- **RAG 기반 검색**: 벡터 임베딩을 활용한 의미 기반 문서 검색
- **키워드 매핑**: 제품과 관련 키워드 자동 매핑 시스템
- **실시간 검색**: React 기반 반응형 사용자 인터페이스
- **벡터 데이터베이스**: Qdrant를 통한 고성능 벡터 검색
- **컨테이너화**: Docker를 통한 간편한 배포 및 확장

## 🛠️ 기술 스택

### Backend
- **Python 3.9+**
- **FastAPI** - 고성능 웹 프레임워크
- **Qdrant** - 벡터 데이터베이스
- **Transformers** - 자연어 처리 모델

### Frontend
- **React 18** - 사용자 인터페이스 라이브러리
- **JavaScript (ES6+)**
- **CSS3** - 스타일링

### 개발 도구
- **Docker & Docker Compose** - 컨테이너화
- **ESLint** - JavaScript 코드 품질 검사
- **Prettier** - 코드 포맷팅
- **Black & Flake8** - Python 코드 포맷팅 및 검사
- **Husky** - Git hooks 자동화
- **Commitlint** - 커밋 메시지 규칙

## 📦 설치 및 실행

### Prerequisites
- Node.js 16+
- Python 3.9+
- Docker & Docker Compose (선택사항)

### 로컬 개발 환경 설정

1. **저장소 클론**
   ```bash
   git clone https://github.com/RISK-KILLER/PROJECT_FDA.git
   cd PROJECT_FDA
   ```

2. **백엔드 설정**
   ```bash
   cd backend
   pip install -r requirements.txt
   python main.py
   ```

3. **프론트엔드 설정**
   ```bash
   cd frontend
   npm install
   npm start
   ```

4. **개발 도구 설정**
   ```bash
   # 프로젝트 루트에서
   pre-commit install
   npm install -g @commitlint/cli @commitlint/config-conventional

   # 백엔드 코드 품질 도구
   cd backend
   pip install black isort flake8
   ```

### Docker를 사용한 실행

```bash
# 전체 스택 실행
docker-compose up -d

# 개별 서비스 실행
docker-compose up backend
docker-compose up frontend
```

## 🔧 개발 환경

이 프로젝트는 팀 협업을 위한 프로페셔널한 개발 환경을 구축했습니다:

### 코드 품질 관리
- **Pre-commit Hooks**: 커밋 전 자동 코드 검사
- **ESLint**: JavaScript/React 코드 품질 검사
- **Prettier**: 일관된 코드 포맷팅
- **Black & Flake8**: Python 코드 스타일 통일

### 커밋 규칙
프로젝트는 Conventional Commits 규칙을 따릅니다:

```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 변경
style: 코드 포맷팅 (기능 변경 없음)
refactor: 코드 리팩터링
test: 테스트 추가/수정
chore: 빌드 과정이나 보조 도구 변경
```

예시: `feat: RAG 검색 성능 최적화`

## 🔗 API 엔드포인트

### 주요 API
- `GET /` - 서버 상태 확인
- `POST /search` - RAG 기반 검색 요청
- `GET /keywords` - 키워드 매핑 조회
- `POST /keywords` - 키워드 매핑 업데이트

상세한 API 문서는 서버 실행 후 `/docs`에서 확인할 수 있습니다.

## 📊 데이터 구조

### 키워드 매핑 (product_keyword_mappings.json)
```json
{
  "product_category": {
    "keywords": ["keyword1", "keyword2"],
    "descriptions": "제품 설명",
    "regulations": ["관련 규정 정보"]
  }
}
```

## 🤝 기여 방법

1. **이슈 생성**: 버그 리포트나 기능 요청
2. **브랜치 생성**: `git checkout -b feature/새기능`
3. **커밋**: `git commit -m "feat: 새로운 기능 추가"`
4. **푸시**: `git push origin feature/새기능`
5. **Pull Request 생성**

### 개발 가이드라인
- 모든 코드는 pre-commit 검사를 통과해야 함
- 커밋 메시지는 Conventional Commits 규칙 준수
- 새로운 기능은 테스트 코드와 함께 제출
- PR은 코드 리뷰 후 머지

## 📈 향후 계획

- [ ] 자동화된 테스트 추가
- [ ] CI/CD 파이프라인 구축
- [ ] 다국어 지원
- [ ] 성능 모니터링 시스템
- [ ] 사용자 인증 시스템
- [ ] API 캐싱 최적화

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 있습니다.

## 👥 팀

**RISK-KILLER Organization**
- 프로젝트 리더: [@seungmin956](https://github.com/seungmin956)

## 📞 문의

프로젝트 관련 문의사항이 있으시면 Issues 탭을 활용해 주세요.

---

*이 프로젝트는 RAG 기술을 활용한 FDA 수출 지원 서비스 구축을 목표로 합니다.*
