from enum import StrEnum
from typing import Annotated

from fastapi import FastAPI, Query


class TaskState(StrEnum):
    QUEUED = "queued"
    RUNNING = "running"
    DONE = "done"


TASKS = [
    {"id": 1, "title": "FastAPI 서버 실행하기", "state": TaskState.DONE},
    {"id": 2, "title": "경로 매개변수로 할 일 조회하기", "state": TaskState.RUNNING},
    {"id": 3, "title": "API 요청 기록하기", "state": TaskState.QUEUED},
    {"id": 4, "title": "API 응답 점검하기", "state": TaskState.QUEUED},
    {"id": 5, "title": "쿼리 조건 정리하기", "state": TaskState.RUNNING},
    {"id": 6, "title": "문서 확인하기", "state": TaskState.DONE},
]

app = FastAPI(title="Task Search and Paging API")

@app.get("/tasks")
def list_tasks(
    state: Annotated[TaskState | None, Query(description="작업 상태")] = None,
    keyword: Annotated[str | None, Query(description="제목 검색기")] = None,
    offset: Annotated[int, Query(ge = 0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10
) -> dict:
    """조건에 맞는 작업을 고른 뒤 필요한 구간만 반환한다."""
    matched = TASKS if state is None else [task for task in TASKS if task["state"] == state]
    if keyword is not None:
        matched = [task for task in matched if keyword.casefold() in task["title"].casefold()]

    total = len(matched)
    items = matched[offset : offset + limit]
    
    return {"keyword":keyword, "items":items, "total": total}