"""공통 조회 조건을 의존성으로 분리한다."""

from typing import Annotated, Literal

from fastapi import Depends, FastAPI, HTTPException, Path, Query
from fastapi import status as http_status
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Assignment Check Dependency API")


# 앞선 예제의 요청 모델과 입력 검증을 그대로 유지한다.
class RunCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    agent_name: str = Field(min_length=2, max_length=30)
    prompt: str = Field(min_length=1, max_length=500)
    max_attempts: int = Field(default=3, ge=1, le=5)
    tags: list[str] = Field(default_factory=list, max_length=5)
    timeout_seconds: int = Field(default=30, ge=1, le=120)

    @field_validator("tags")
    def normalize_tags(tags: list[str]) -> list[str]:
        """태그의 공백·대소문자·중복을 정리한다."""
        normalized: list[str] = []
        for tag in tags:
            cleaned = tag.strip().casefold()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized


class RunPublic(BaseModel):
    id: int
    agent_name: str
    status: Literal["queued", "running", "done", "failed"]
    result: str | None


class RunSummary(BaseModel):
    id: int
    agent_name: str
    status: Literal["queued", "running", "done", "failed"]


class RunList(BaseModel):
    items: list[RunSummary]
    total: int


# 여러 쿼리를 하나의 의존성 결과로 묶는다.
class RunFilters(BaseModel):
    status: str | None
    skip: int
    limit: int


INTERNAL_RUNS: dict[int, dict[str, object]] = {
    1: {
        "id": 1,
        "agent_name": "code-reviewer",
        "status": "done",
        "result": "GET과 POST의 상태 코드 사용을 확인했다",
        "prompt": "제출한 FastAPI 코드에서 상태 코드를 점검한다",
        "max_attempts": 3,
        "tags": ["fastapi"],
        "timeout_seconds": 30,
        "debug_token": "internal-only",
        "operator_note": "수업 확인 완료",
    },
    2: {
        "id": 2,
        "agent_name": "test-runner",
        "status": "queued",
        "result": None,
        "prompt": "API 테스트를 실행한다",
        "max_attempts": 3,
        "tags": ["test"],
        "timeout_seconds": 30,
        "debug_token": "internal-only",
        "operator_note": "실행 대기 중",
    },
    3: {
        "id": 3,
        "agent_name": "code-reviewer",
        "status": "failed",
        "result": "응답 모델에서 필수 id가 누락됐다",
        "prompt": "응답 계약을 점검한다",
        "max_attempts": 3,
        "tags": ["response"],
        "timeout_seconds": 30,
        "debug_token": "internal-only",
        "operator_note": "코드 수정 필요",
    },
}


# Depends에는 이 함수를 호출한 결과가 아니라 함수 자체를 전달한다.
# 요청이 들어오면 FastAPI가 쿼리를 검증한 뒤 이 함수를 실행한다.
def get_run_filters(
    status: Annotated[str | None, Query(min_length=2, max_length=20)] = None,
    skip: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> RunFilters:
    """공통 쿼리를 검사하고 두 목록 경로가 사용할 객체를 만든다."""
    return RunFilters(
        status=status.casefold() if status is not None else None,
        skip=skip,
        limit=limit,
    )


def select_runs(
    
) -> dict[str, object]:
    """의존성이 준비한 조건을 내부 실행 기록에 적용한다."""
    return {}


# 생성 경로를 그대로 유지한다.
@app.post("/runs", response_model=RunPublic, status_code=http_status.HTTP_201_CREATED)
def create_run(run: RunCreate) -> dict[str, object]:
    """검증된 요청을 내부 기록으로 저장하고 공개 필드만 응답한다."""
    run_id = max(INTERNAL_RUNS, default=0) + 1
    record: dict[str, object] = {
        "id": run_id,
        **run.model_dump(),
        "status": "queued",
        "result": None,
        "debug_token": "internal-only",
        "operator_note": "",
    }
    INTERNAL_RUNS[run_id] = record
    return record


@app.get("/runs", response_model=RunList)
def list_runs(

) -> dict[str, object]:
    """공통 조회 조건으로 전체 실행 목록을 조회한다."""
    return {}

@app.get("/agents/{agent_name}/runs", response_model=RunList)
def list_agent_runs(
    agent_name: Annotated[str, Path(min_length=2, max_length=30)],

) -> dict[str, object]:
    """한 에이전트의 실행 목록에 같은 조회 조건을 적용한다."""
    return {}


# 상세 조회도 그대로 유지한다.
@app.get("/runs/{run_id}", response_model=RunPublic)
def read_run(run_id: Annotated[int, Path(ge=1)]) -> dict[str, object]:
    """번호와 일치하는 내부 기록을 상세 공개 모델로 반환한다."""
    run = INTERNAL_RUNS.get(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="실행 기록을 찾을 수 없다")
    return run