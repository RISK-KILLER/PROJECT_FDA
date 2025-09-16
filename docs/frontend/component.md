# Frontend Component Architecture

## Overview
프론트엔드는 React 기반으로 구성되어 있으며, 컴포넌트 분리를 통해 유지보수성과 재사용성을 높였습니다.

## Component Structure

### 1. App.js (Main Container)
- **역할**: 전체 애플리케이션의 상태 관리 및 컴포넌트 조합
- **주요 상태**: 
  - `projects`: 프로젝트 목록
  - `messages`: 현재 프로젝트의 메시지
  - `inputMessage`: 입력창 텍스트
  - `isTyping`: AI 응답 생성 중 상태
- **주요 기능**:
  - 프로젝트 생성/선택/삭제
  - 메시지 전송 및 API 호출
  - 파일 업로드 처리
  - 대화 초기화

### 2. Sidebar.jsx
- **역할**: 좌측 프로젝트 관리 패널
- **Props**:
  - `projects`: 프로젝트 목록
  - `onCreateProject`: 새 프로젝트 생성 콜백
  - `onSelectProject`: 프로젝트 선택 콜백
  - `onDeleteProject`: 프로젝트 삭제 콜백
- **기능**:
  - 프로젝트 목록 표시
  - 새 프로젝트 생성 버튼
  - 프로젝트 선택/삭제 UI

### 3. MessageList.jsx (Memoized)
- **역할**: 채팅 메시지 목록 렌더링
- **Props**:
  - `messages`: 메시지 배열
  - `isTyping`: 타이핑 상태
  - `onGenerateChecklist`: 체크리스트 생성 콜백
  - `onDownloadReport`: 보고서 다운로드 콜백
  - `setInputMessage`: 입력창 텍스트 설정 콜백
  - `sendMessage`: 메시지 전송 콜백
- **최적화**: `React.memo`로 불필요한 리렌더 방지
- **하위 컴포넌트**:
  - `PromptChips`: 프롬프트 칩 UI
  - `ScenarioCards`: 시나리오 카드 UI
  - `SampleSnippets`: 예시 대화 스니펫 UI

### 4. InputBar.jsx
- **역할**: 메시지 입력 및 파일 업로드 영역
- **Props**:
  - `inputMessage`: 입력창 텍스트
  - `setInputMessage`: 입력창 텍스트 설정 콜백
  - `isTyping`: 타이핑 상태
  - `onSend`: 메시지 전송 콜백
  - `onKeyPress`: 키보드 이벤트 핸들러
  - `onDrop`, `onDragOver`, `onDragLeave`: 드래그 앤 드롭 핸들러
  - `dragOver`: 드래그 상태
  - `fileInputRef`: 파일 입력 참조
  - `onFileChange`: 파일 변경 핸들러

### 5. PromptChips.jsx
- **역할**: 프롬프트 칩 및 "바로 질문" 액션
- **Props**:
  - `chips`: 칩 데이터 배열
  - `setInputMessage`: 입력창 텍스트 설정 콜백
  - `sendMessage`: 메시지 전송 콜백
- **기능**:
  - 칩 클릭 시 입력창에 프롬프트 채우기
  - "바로 질문" 버튼으로 즉시 전송

### 6. ScenarioCards.jsx
- **역할**: 시나리오 카드 UI
- **Props**:
  - `scenarios`: 시나리오 데이터 배열
  - `setInputMessage`: 입력창 텍스트 설정 콜백
  - `sendMessage`: 메시지 전송 콜백
- **기능**:
  - 시나리오 제목, 요약 표시
  - "예시 질문 넣기" / "바로 질문" 버튼

### 7. SampleSnippets.jsx
- **역할**: 예시 대화 스니펫 표시
- **Props**:
  - `samples`: 샘플 대화 데이터 배열
- **기능**:
  - USER/BOT 대화 예시 표시

## Component Design Principles

### 1. 단일 책임 원칙
- 각 컴포넌트는 하나의 명확한 역할을 담당
- UI 로직과 비즈니스 로직 분리

### 2. Props를 통한 데이터 전달
- 상위 컴포넌트에서 상태 관리
- 하위 컴포넌트는 props로 데이터 수신
- 콜백 함수를 통한 상위 컴포넌트와의 통신

### 3. 조건부 렌더링
- 데이터가 없을 때는 컴포넌트를 렌더링하지 않음
- `if (!data || data.length === 0) return null;` 패턴 사용

### 4. 성능 최적화
- `React.memo`를 통한 불필요한 리렌더 방지
- 메시지 목록과 같은 자주 업데이트되는 컴포넌트에 적용

## File Structure
```
frontend/src/
├── App.js                    # 메인 컨테이너
├── components/
│   ├── Sidebar.jsx          # 프로젝트 관리 패널
│   ├── MessageList.jsx      # 메시지 목록 (메모화됨)
│   ├── InputBar.jsx         # 입력 영역
│   ├── PromptChips.jsx      # 프롬프트 칩
│   ├── ScenarioCards.jsx    # 시나리오 카드
│   └── SampleSnippets.jsx   # 예시 대화 스니펫
└── App.css
```

## Usage Guidelines

### 1. 새 컴포넌트 추가 시
- 단일 책임 원칙 준수
- Props 타입 명시 (향후 TypeScript 도입 시)
- 조건부 렌더링 패턴 적용

### 2. 성능 최적화
- 자주 리렌더되는 컴포넌트는 `React.memo` 적용 검토
- 콜백 함수는 `useCallback`으로 메모화 고려

### 3. 상태 관리
- 로컬 상태는 해당 컴포넌트에서 관리
- 공유 상태는 가장 가까운 공통 조상에서 관리
- 복잡한 상태는 Context API 또는 상태 관리 라이브러리 고려

## Future Improvements

### 1. TypeScript 도입
- Props 타입 정의
- 컴포넌트 인터페이스 명확화

### 2. 테스트 추가
- 각 컴포넌트별 단위 테스트
- 통합 테스트

### 3. 가상 스크롤
- 메시지 수가 많아질 경우 `react-window` 도입 고려

### 4. 상태 관리 라이브러리
- 프로젝트 규모가 커질 경우 Redux Toolkit 또는 Zustand 도입 검토
