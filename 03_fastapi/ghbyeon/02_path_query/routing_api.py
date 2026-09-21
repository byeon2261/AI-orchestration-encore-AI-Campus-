from typing import Annotated
from enum import StrEnum
from fastapi import FastAPI, Body, HTTPException, Path, Query, status

# StrEnum은 문자열처럼 사용할 수 있는 상태값을 미리 정해둔다.
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

app = FastAPI(title="Task Routing API")

@app.get("/tasks")
def list_tasks(
    state: Annotated[TaskState | None, Query(description="필터링할 작업 상태")] = None,
    limit: Annotated[int , Query(ge=1, le=20)] =10,
) -> dict:
    tasks = TASKS if state is None else [task for task in TASKS if task["state"] == state]
    return {"items": tasks[:limit], "total": len(tasks)}

@app.get("/tasks/{task_id}")
def read_task(task_id: Annotated[int, Path(ge=1)]) -> dict:
    """주소의  ID와 일치하는 할 일 하나를 반환한다."""
    # next는 첫 일치 항목을 찾고, 없으면 None을 반환한다.
    task = next((task for task in TASKS if task ["id"] == task_id), None)
    if task is None:
        raise HTTPException(status_code=404, detail="할 일을 찾을 수 없다.")
    return task