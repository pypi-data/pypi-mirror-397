"""
Work Assistant MCP Server

프로세스 조회, 회사 정보 질의를 위한 MCP 도구 모음.
Agent가 사용자 요청을 분석하고 필요한 도구를 선택해서 호출합니다.
실제 프로세스 실행은 프론트엔드에서 처리합니다.
"""

import os
import json
import httpx
from typing import Optional, List
from fastmcp import FastMCP
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

# Supabase 설정
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# FastMCP 서버 생성
mcp = FastMCP(
    "work-assistant",
    instructions="""
    이 서버는 업무 지원을 위한 조회 도구들을 제공합니다.
    
    주요 기능:
    1. 프로세스 목록/상세 조회 - 회사에 정의된 업무 프로세스 조회
    2. 폼 필드 조회 - 프로세스 실행에 필요한 입력 폼 정보
    3. 인스턴스/할일 조회 - 진행 중인 업무 현황 확인
    4. 조직도 조회 - 회사 조직 구조 확인
    
    모든 조회에는 tenant_id(테넌트 식별자)가 필요합니다.
    
    ※ 프로세스 실행은 이 도구에서 하지 않습니다.
      Agent가 필요한 정보(process_id, form_fields)를 조회한 후,
      프론트엔드에서 실제 실행을 처리합니다.
    """
)


def get_supabase_headers() -> dict:
    """Supabase API 호출용 헤더 생성"""
    return {
        "apikey": SUPABASE_SERVICE_KEY,
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }


# =============================================================================
# 도구 1: 프로세스 목록 조회
# =============================================================================
@mcp.tool()
async def get_process_list(tenant_id: str) -> str:
    """
    프로세스 정의 목록을 조회합니다.
    
    사용자가 "어떤 프로세스가 있어?", "업무 목록 보여줘" 등을 요청할 때 사용합니다.
    프로세스 실행 전에 어떤 프로세스가 있는지 확인할 때도 사용합니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인, 예: "uengine")
    
    Returns:
        프로세스 목록 JSON 문자열. 각 프로세스는 id, name, description을 포함합니다.
        예: [{"id": "vacation_request", "name": "휴가신청", "description": "연차/반차 신청 프로세스"}, ...]
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/proc_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "select": "id,name,description"
                }
            )
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 2: 프로세스 상세 조회
# =============================================================================
@mcp.tool()
async def get_process_detail(tenant_id: str, process_id: str) -> str:
    """
    특정 프로세스의 상세 정보를 조회합니다.
    
    프로세스 실행 전에 어떤 단계가 있는지, 첫 번째 액티비티가 뭔지 확인할 때 사용합니다.
    사용자가 "휴가신청 프로세스 어떻게 진행돼?" 등을 물어볼 때 사용합니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        process_id: 프로세스 정의 ID (get_process_list에서 얻은 id 값)
    
    Returns:
        프로세스 상세 정보 JSON. definition 필드에 activities(단계), roles(역할), 
        events(시작/종료 이벤트), sequences(흐름) 등이 포함됩니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/proc_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "id": f"eq.{process_id}",
                    "select": "id,name,description,definition"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return json.dumps(data[0], ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "프로세스를 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 3: 폼 필드 조회
# =============================================================================
@mcp.tool()
async def get_form_fields(tenant_id: str, form_key: str) -> str:
    """
    폼의 입력 필드 정보를 조회합니다.
    
    프로세스 실행 시 사용자에게 어떤 입력을 받아야 하는지 확인할 때 사용합니다.
    form_key는 보통 "{process_id}_{activity_id}_form" 형식입니다.
    get_process_detail의 definition.activities에서 tool 필드를 확인하면 됩니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        form_key: 폼 키 (예: "vacation_request_activity_001_form")
    
    Returns:
        폼 필드 정보 JSON. html(폼 HTML), fields_json(필드 상세 정보)를 포함합니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/form_def",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "id": f"eq.{form_key}",
                    "select": "id,name,html,fields_json,proc_def_id,activity_id"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                return json.dumps(data[0], ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "폼을 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 4: 인스턴스 목록 조회
# =============================================================================
@mcp.tool()
async def get_instance_list(tenant_id: str, user_id: str, process_id: Optional[str] = None) -> str:
    """
    진행 중인 프로세스 인스턴스(업무) 목록을 조회합니다.
    
    사용자가 "내 진행 중인 업무", "휴가신청 현황" 등을 물어볼 때 사용합니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        user_id: 사용자 ID (참여자로 필터링)
        process_id: (선택) 특정 프로세스로 필터링할 경우 프로세스 ID
    
    Returns:
        인스턴스 목록 JSON. 각 인스턴스는 proc_inst_id, proc_def_id, status, 
        start_date, participants, current_activity_ids 등을 포함합니다.
    """
    try:
        params = {
            "tenant_id": f"eq.{tenant_id}",
            "participants": f"cs.{{{user_id}}}",  # contains user_id
            "select": "proc_inst_id,proc_def_id,proc_inst_name,status,start_date,end_date,due_date,participants,current_activity_ids,variables_data"
        }
        
        if process_id:
            params["proc_def_id"] = f"eq.{process_id}"
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/bpm_proc_inst",
                headers=get_supabase_headers(),
                params=params
            )
            response.raise_for_status()
            data = response.json()
            return json.dumps(data, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 5: 할 일 목록 조회
# =============================================================================
@mcp.tool()
async def get_todolist(tenant_id: str, instance_ids: List[str]) -> str:
    """
    특정 인스턴스들의 할 일(activity) 목록을 조회합니다.
    
    사용자가 "이 업무 현재 어떤 단계야?", "할 일 목록 보여줘" 등을 물어볼 때 사용합니다.
    get_instance_list로 인스턴스 ID를 먼저 얻은 후 사용합니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
        instance_ids: 조회할 인스턴스 ID 목록 (get_instance_list에서 얻은 proc_inst_id 값들)
    
    Returns:
        할 일 목록 JSON. 프로세스별, 인스턴스별로 그룹화된 activity 정보를 포함합니다.
    """
    try:
        if not instance_ids:
            return json.dumps({"error": "instance_ids가 비어있습니다."}, ensure_ascii=False)
        
        # instance_ids를 쉼표로 구분된 문자열로 변환
        ids_filter = ",".join([f'"{id}"' for id in instance_ids])
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/todolist",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "proc_inst_id": f"in.({ids_filter})",
                    "select": "proc_inst_id,proc_def_id,activity_id,activity_name,start_date,end_date,status,description,user_id",
                    "order": "start_date.asc"
                }
            )
            response.raise_for_status()
            todos = response.json()
            
            # 프로세스별, 인스턴스별로 그룹화
            result = {}
            for todo in todos:
                def_id = todo.get("proc_def_id", "unknown")
                inst_id = todo.get("proc_inst_id", "unknown")
                
                if def_id not in result:
                    result[def_id] = {"processDefinitionId": def_id, "instances": {}}
                
                if inst_id not in result[def_id]["instances"]:
                    result[def_id]["instances"][inst_id] = {"instanceId": inst_id, "activities": []}
                
                result[def_id]["instances"][inst_id]["activities"].append({
                    "activityId": todo.get("activity_id"),
                    "activityName": todo.get("activity_name"),
                    "status": todo.get("status"),
                    "startDate": todo.get("start_date"),
                    "endDate": todo.get("end_date"),
                    "userId": todo.get("user_id")
                })
            
            return json.dumps(result, ensure_ascii=False, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 도구 6: 조직도 조회
# =============================================================================
@mcp.tool()
async def get_organization(tenant_id: str) -> str:
    """
    회사 조직도를 조회합니다.
    
    사용자가 "조직도 보여줘", "우리 회사 구조가 어떻게 돼?" 등을 물어볼 때 사용합니다.
    
    Args:
        tenant_id: 테넌트 ID (서브도메인)
    
    Returns:
        조직도 정보 JSON. 부서, 팀, 직원 계층 구조를 포함합니다.
    """
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{SUPABASE_URL}/rest/v1/configuration",
                headers=get_supabase_headers(),
                params={
                    "tenant_id": f"eq.{tenant_id}",
                    "key": "eq.organization",
                    "select": "value"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                value = data[0].get("value", {})
                chart = value.get("chart", value) if isinstance(value, dict) else value
                return json.dumps(chart, ensure_ascii=False, indent=2)
            else:
                return json.dumps({"error": "조직도 정보를 찾을 수 없습니다."}, ensure_ascii=False)
    except Exception as e:
        return json.dumps({"error": str(e)}, ensure_ascii=False)


# =============================================================================
# 메인 진입점
# =============================================================================
def main():
    """MCP 서버 실행"""
    mcp.run()


if __name__ == "__main__":
    main()
