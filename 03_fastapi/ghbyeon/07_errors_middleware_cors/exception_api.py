"""예상 가능한 업무 예외를 일관된 HTTP 응답으로 바꾼다."""

from typing import Literal

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


class TaskNotFoundException(Exception):
    """요청한 작업이 저장소에 없다는 업무 상황을 표현한다."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id

class TaskTitleConflictException(Exception):
    """같은 제목의 작업을 다시 등록하려는 없무 상황을 표현한다."""
    def __init__(self, title: str) -> None:
        self.title  = title

class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=30)


class TaskResponse(BaseModel):
    id: int
    title: str
    status: Literal["todo"]

# 클라이언트에게 공개할 공통 오류 본문
class ErrorResponse(BaseModel):
    error: str
    message: str

app = FastAPI(title="Task Error Handling API")

# 서버 메모리에만 있으므로 재시작하면 처음 상태로 돌아간다.
TASKS: dict[int, dict[str, object]] = {
    1: {"id": 1, "title": "예외 처리 흐름 확인", "status": "todo"},
}    

# TaskNotFoundException이 발생했을 때 이 함수가 실행된다. (예외 처리)
@app.exception_handler(TaskNotFoundException)
def task_not_found_handler(
    _request: Request,
    error: TaskNotFoundException
) -> JSONResponse:
    body = ErrorResponse(
        error= "task_not_found",
        message= f"작업 {error.task_id}번을 찾을 수 없습니다."
    )
    return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content=body.model_dump())

@app.exception_handler(TaskTitleConflictException)
def task_title_conflict_exception(
    _request: Request,
    error: TaskTitleConflictException
) -> JSONResponse:
    pass


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int) -> dict[str, object]:
    task = TASKS.get(task_id)
    if task is None:
        raise TaskNotFoundException(task_id)
    return task


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task_create: TaskCreate) -> dict[str, object]:
    normalized_title = task_create.title.casefold()
    if any(str(task["title"]).casefold() == normalized_title for task in TASKS.values()):
        pass

    task_id = max(TASKS, default=0) + 1
    task = {"id": task_id, "title": task_create.title, "status": "todo"}
    TASKS[task_id] = task
    return task