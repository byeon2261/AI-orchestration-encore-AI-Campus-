"""기능은 완성되어 있고 OpenAPI 문서 정보를 보강할 FastAPI 예제다."""

from typing import Annotated, Literal

from fastapi import FastAPI, Path, Query, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field


Difficulty = Literal["beginner", "intermediate", "advanced"]
TaskStatus = Literal["planned"]


class StudyTaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=100)
    subject: str = Field(min_length=2, max_length=50)
    difficulty: Difficulty = "beginner"
    estimated_minutes: int = Field(default=30, ge=10, le=240)


class StudyTaskResponse(BaseModel):
    id: int
    title: str
    subject: str
    difficulty: Difficulty
    estimated_minutes: int
    status: TaskStatus


class StudyTaskListResponse(BaseModel):
    items: list[StudyTaskResponse]
    total: int


class ErrorResponse(BaseModel):
    error: str
    message: str


class StudyTaskNotFoundError(Exception):
    pass


class StudyTaskConflictError(Exception):
    pass


app = FastAPI()


# 서버를 다시 시작하면 메모리의 작업 목록도 처음 상태로 돌아간다.
study_tasks = [
    StudyTaskResponse(
        id=1,
        title="FastAPI 문서 확인",
        subject="FastAPI",
        difficulty="beginner",
        estimated_minutes=30,
        status="planned",
    )
]
next_task_id = 2


@app.exception_handler(StudyTaskNotFoundError)
async def task_not_found_handler(
    _request: Request,
    _error: StudyTaskNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=ErrorResponse(
            error="study_task_not_found",
            message="학습 작업을 찾을 수 없다",
        ).model_dump(),
    )


@app.exception_handler(StudyTaskConflictError)
async def task_conflict_handler(
    _request: Request,
    _error: StudyTaskConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=ErrorResponse(
            error="study_task_title_conflict",
            message="같은 제목의 학습 작업이 이미 있다",
        ).model_dump(),
    )


@app.get("/study-tasks")
def list_study_tasks(
    difficulty: Annotated[Difficulty | None, Query()] = None,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> dict[str, object]:
    selected = [
        task
        for task in study_tasks
        if difficulty is None or task.difficulty == difficulty
    ]
    limited = selected[:limit]
    return StudyTaskListResponse(
        items=limited,
        total=len(selected),
    ).model_dump()


@app.post("/study-tasks", status_code=status.HTTP_201_CREATED)
def create_study_task(data: StudyTaskCreate) -> dict[str, object]:
    global next_task_id

    normalized_title = data.title.casefold()
    if any(task.title.casefold() == normalized_title for task in study_tasks):
        raise StudyTaskConflictError

    task = StudyTaskResponse(
        id=next_task_id,
        title=data.title,
        subject=data.subject,
        difficulty=data.difficulty,
        estimated_minutes=data.estimated_minutes,
        status="planned",
    )
    study_tasks.append(task)
    next_task_id += 1
    return task.model_dump()


@app.get("/study-tasks/{task_id}")
def read_study_task(
    task_id: Annotated[int, Path(ge=1)],
) -> dict[str, object]:
    for task in study_tasks:
        if task.id == task_id:
            return task.model_dump()
    raise StudyTaskNotFoundError