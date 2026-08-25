"""
초보자용 데모 서버
-------------------------------------------------
목적: URL의 파라미터(tasks)를 분석해서, 어떤 agent에게
      어떤 keyword로 작업을 시킬지 서버가 파싱하고 실행한다.

호출 예시:
    http://localhost:8000/run?tasks=kostat:30대여성_커피;weather:서울

동작 흐름:
    1. tasks 파라미터를 받는다  ->  "kostat:30대여성_커피;weather:서울"
    2. ';' 기준으로 여러 작업(task)으로 나눈다
    3. 각 작업을 ':' 기준으로 agent 이름과 keyword로 나눈다
    4. agent 이름에 맞는 처리 함수를 찾아서 실행한다 (지금은 mock)
    5. 모든 결과를 모아서 JSON으로 응답한다
"""

from fastapi import FastAPI, Query
from typing import List, Dict

app = FastAPI(title="Agent Dispatcher Demo")


# -------------------------------------------------
# 1. agent별 처리 함수 (지금은 진짜 API 대신 '가짜 응답' = mock)
#    나중에 이 함수 내용만 실제 API 호출 코드로 바꾸면 됨
# -------------------------------------------------

def run_kostat_agent(keyword: str) -> Dict:
    """국가통계청(KOSIS) 관련 agent - 지금은 mock"""
    return {
        "agent": "kostat",
        "keyword": keyword,
        "status": "mock",
        "result": f"[mock] '{keyword}' 관련 국가통계 데이터를 여기에 채울 예정입니다."
    }


def run_weather_agent(keyword: str) -> Dict:
    """날씨 관련 agent - 지금은 mock"""
    return {
        "agent": "weather",
        "keyword": keyword,
        "status": "mock",
        "result": f"[mock] '{keyword}' 지역의 날씨 데이터를 여기에 채울 예정입니다."
    }


# -------------------------------------------------
# 2. agent 이름 -> 처리 함수를 연결해주는 '지도(map)'
#    새로운 agent를 추가하고 싶으면
#    (1) 위처럼 run_xxx_agent 함수를 만들고
#    (2) 아래 딕셔너리에 한 줄만 추가하면 됨
# -------------------------------------------------

AGENT_MAP = {
    "kostat": run_kostat_agent,
    "weather": run_weather_agent,
}


# -------------------------------------------------
# 3. tasks 문자열을 파싱하는 함수
#    "kostat:30대여성_커피;weather:서울"
#    ->  [("kostat", "30대여성_커피"), ("weather", "서울")]
# -------------------------------------------------

def parse_tasks(tasks: str) -> List[tuple]:
    parsed = []
    # ';' 기준으로 각 작업 분리
    task_items = tasks.split(";")

    for item in task_items:
        item = item.strip()
        if not item:
            continue  # 빈 값은 건너뜀

        # ':' 기준으로 agent 이름과 keyword 분리
        if ":" not in item:
            # 형식이 잘못된 경우 (예: ':' 없이 들어온 경우) 건너뜀
            continue

        agent_name, keyword = item.split(":", 1)  # 맨 첫 ':' 기준으로만 분리
        parsed.append((agent_name.strip(), keyword.strip()))

    return parsed


# -------------------------------------------------
# 4. 실제 URL 엔드포인트
#    브라우저에서 이 주소로 접속하면 아래 함수가 실행됨
# -------------------------------------------------

@app.get("/run")
def run(tasks: str = Query(..., description="예: kostat:30대여성_커피;weather:서울")):
    parsed_tasks = parse_tasks(tasks)

    results = []
    errors = []

    for agent_name, keyword in parsed_tasks:
        agent_function = AGENT_MAP.get(agent_name)

        if agent_function is None:
            # 등록되지 않은 agent 이름이 들어온 경우
            errors.append(f"'{agent_name}'라는 agent는 아직 등록되어 있지 않습니다.")
            continue

        result = agent_function(keyword)
        results.append(result)

    return {
        "input_tasks": tasks,
        "parsed_count": len(parsed_tasks),
        "results": results,
        "errors": errors,
    }


# -------------------------------------------------
# 5. 서버 상태 확인용 기본 페이지 (선택 사항)
# -------------------------------------------------

@app.get("/")
def health_check():
    return {"status": "ok", "message": "서버가 정상적으로 실행 중입니다."}