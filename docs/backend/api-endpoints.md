# API Endpoints

## Chat Endpoint
### POST /api/chat
채팅 메시지를 받아 ReAct Agent를 통해 FDA 규제 답변을 생성합니다.

**Request:**
```json
{
  "message": "김치 수출 규제에 대해 알려주세요",
  "project_id": 1,
  "language": "ko"
}
```

**Response:**
```json
{
  "content": "김치는 발효식품으로 분류되어...",
  "keywords": ["kimchi", "fermented food"],
  "cfr_references": [
    {
      "title": "21 CFR 101 - Food Labeling",
      "description": "관련 규정/자료",
      "url": "https://www.ecfr.gov/current/title-21/chapter-I/subchapter-B/part-101"
    }
  ],
  "sources": ["21 CFR 101 - Food Labeling"],
  "citations": [],
  "responseTime": 1234.56,
  "agentResponseTime": 1100.23,
  "timestamp": "2024-10-24T14:30:00.000000"
}
```

## Project Management Endpoints

### DELETE /api/project/{project_id}
특정 프로젝트를 삭제하고 해당 에이전트 인스턴스를 제거합니다.

**Response:**
```json
{
  "message": "프로젝트가 삭제되었습니다."
}
```

### POST /api/project/{project_id}/reset
특정 프로젝트의 대화 히스토리를 초기화합니다.

**Response:**
```json
{
  "message": "대화 히스토리가 초기화되었습니다."
}
```

또는 프로젝트가 없을 경우:
```json
{
  "message": "새로운 대화가 시작되었습니다."
}
```

## Health Check
### GET /
서버 상태 확인용 엔드포인트

**Response:**
```json
{
  "message": "FDA Export Assistant API - ReAct Agent"
}
```

## 주요 특징
- **프로젝트별 에이전트**: 각 프로젝트마다 독립적인 Agent 인스턴스 생성
- **대화 기록 관리**: 프로젝트별 대화 히스토리 유지
- **응답 시간 측정**: 총 응답 시간과 Agent 실행 시간 별도 제공
- **에러 처리**: 사용자 친화적인 에러 메시지 반환