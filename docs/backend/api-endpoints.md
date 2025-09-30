## backend/api-endpoints.md

```markdown
# API Endpoints

## Chat Endpoint
### POST /api/chat
채팅 메시지를 받아 ReAct Agent를 통해 FDA 규제 답변을 생성합니다.

**Request:**
```json
{
  "message": "김치 수출 규제에 대해 알려주세요",
  "project_id": 1
}
```

**Response:**
```json
{
  "content": "김치는 발효식품으로 분류되어...",
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