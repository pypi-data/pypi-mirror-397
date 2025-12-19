# Work Assistant MCP Server

업무 지원을 위한 MCP (Model Context Protocol) 조회 도구 서버입니다.

## 개념

```
사용자 메시지 → Agent (LLM) → MCP 도구 호출 → 결과 반환 → 프론트엔드에서 액션 수행
```

- **MCP** = 조회용 도구 모음 (데이터만 가져옴)
- **프론트엔드** = 실제 액션 수행 (프로세스 실행, 컨설팅 시작 등)

## 도구 목록 (6개)

| 도구명 | 설명 | 입력 |
|--------|------|------|
| `get_process_list` | 프로세스 정의 목록 조회 | `tenant_id` |
| `get_process_detail` | 프로세스 상세 정보 조회 | `tenant_id`, `process_id` |
| `get_form_fields` | 폼 필드 정보 조회 | `tenant_id`, `form_key` |
| `get_instance_list` | 진행 중인 인스턴스 조회 | `tenant_id`, `user_id`, `process_id`(선택) |
| `get_todolist` | 할 일 목록 조회 | `tenant_id`, `instance_ids[]` |
| `get_organization` | 조직도 조회 | `tenant_id` |

## 설치

```bash
cd work-assistant-mcp
pip install -e .
```

## 환경 변수 설정

`env.example.txt`를 참고하여 `.env` 파일을 생성하세요:

```bash
# Supabase 설정
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_KEY=your-service-role-key
```

## 테스트

### MCP Inspector로 테스트
```bash
npx @modelcontextprotocol/inspector python -m work_assistant_mcp.server
```

### FastMCP dev 모드
```bash
fastmcp dev src/work_assistant_mcp/server.py
```

## Cursor에서 사용

`.cursor/mcp.json` 파일에 추가:

```json
{
  "mcpServers": {
    "work-assistant": {
      "command": "python",
      "args": ["-m", "work_assistant_mcp.server"],
      "env": {
        "SUPABASE_URL": "https://your-project.supabase.co",
        "SUPABASE_SERVICE_KEY": "your-key"
      }
    }
  }
}
```

## 사용 시나리오 예시

### 시나리오 1: 프로세스 실행 요청
```
사용자: "휴가 신청해줘"

Agent → get_process_list(tenant_id="uengine")
     → "휴가신청" 프로세스 ID 찾음: "vacation"
     
Agent → get_process_detail(tenant_id="uengine", process_id="vacation")
     → 첫 번째 액티비티, 폼 키 확인
     
Agent → get_form_fields(tenant_id="uengine", form_key="vacation_activity_001_form")
     → 폼 필드 정보 획득
     
Agent: 동작 종료, 결과 반환
     → { intent: "execute", processId: "vacation", formFields: {...} }
     
프론트엔드: 폼 렌더링 → 사용자 입력 → backend.start() 호출
```

### 시나리오 2: 업무 현황 조회
```
사용자: "내 진행 중인 업무 뭐가 있어?"

Agent → get_instance_list(tenant_id="uengine", user_id="user123")
     → 인스턴스 목록 획득
     
Agent → get_todolist(tenant_id="uengine", instance_ids=["inst1", "inst2"])
     → 상세 할 일 목록 획득
     
Agent: 결과를 사용자에게 답변
```

### 시나리오 3: 조직도 조회
```
사용자: "우리 회사 조직도 보여줘"

Agent → get_organization(tenant_id="uengine")
     → 조직도 정보 획득
     
Agent: 결과를 사용자에게 답변
```
