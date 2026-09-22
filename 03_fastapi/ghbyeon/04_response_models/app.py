from fastapi import FastAPI, status
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Literal


app= FastAPI(title="Assignment Check Response API")

class RunCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    agent_name: str = Field(min_length=2, max_length=30, examples=["code-reviewer"])
    prompt: str = Field(min_length=1, max_length=500)
    max_attempts: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list, max_length=5)
    timeout_seconds: int = Field(default=30, ge=1, le=120)

    @field_validator("tags")
    def normalize_tags(tags: list[str]) -> list[str]:
        """빈 태그를 빼고 공백/대소문자/중복을 정리한다."""
        normalized: list[str] = []
        for tag in tags:
            cleaned = tag.strip().casefold()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

# 한 번의 실행 정보 공개 응답 설정
# Literal: status가 네 문자열 중 하나여야 한다는 의미
class RunPublic(BaseModel):
    id: int
    agent_name: str
    status: Literal["queued", "running", "done", "failed"]
    result: str | None

# 여러 번의 실행 정보 공개 응답 설정
class RunSummary(BaseModel):
    id: int
    agent_name:str
    status: Literal["queued", "running", "done", "failed"]

class RunList(BaseModel):
    items: list[RunSummary]
    total: int

INTERNAL_RUNS: dict[int, dict[str, object]] = {
    1: {
        "id": 1,
        "agent_name": "code-reviewer",
        "status": "done",
        "result": "GET과 POST의 상태 코드 사용을 확인했다",
        "prompt": "제출한 FastAPI 코드에서 GET과 POST의 상태 코드를 점검한다",
        "max_attempts": 3,
        "tags": ["fastapi"],
        "timeout_seconds": 30,
        "debug_token": "internal-only",
        "operator_note": "수업 확인 완료",
    }
}

@app.post("/runs", response_model=RunPublic, status_code=status.HTTP_201_CREATED)
def create_run(
    run: RunCreate
) -> dict:
    """검증된 요청을 내부 기록으로 저장하고 공개 필드만 응답한다."""
    # 초기 기록의 번호는 1이다. 다음 기록은 2부터 시작한다.
    run_id = max(INTERNAL_RUNS, default=0) + 1
    record: dict[str, object] = {
        "id": run_id,
        **run.model_dump(),  # 검증된 입력 필드를 딕셔너리 안에 펼친다.
        "status": "queued",
        "result": None,
        "debug_token": "internal-only",
        "operator_note": "",
    }
    # 반환 전에 저장해야 이후 GET 요청에서 같은 기록을 찾을 수 있다.
    INTERNAL_RUNS[run_id] = record
    # 내부 필드를 포함해 반환해도 FastAPI가 RunPublic에 맞게 걸러 낸다.
    return record

@app.get("/runs", response_model=RunList)
def list_runs() -> dict:
    """저장 된 실행의 짧은 목록과 개수를 보여준다."""
    return {"items": list(INTERNAL_RUNS.values()), "total": len(INTERNAL_RUNS)}

@app.get("/runs/{runs_id}")
def read_run(run_id: int) -> dict:
    """번호로 한 실행을 찾고, 없으면 404로 알린다."""
