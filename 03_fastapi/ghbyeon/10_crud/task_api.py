"""한 파일에서 CRUD의 전체 흐름을 확인하는 작업 API다."""

from fastapi import FastAPI, Request, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

app = FastAPI(title="Task CRUD API", version="0.1.0")


class TaskCreate(BaseModel):
    """POST 요청은 새 작업에 필요한 값만 받는다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=30)

class TaskReplace(BaseModel):
    """PUT 요청은 사용자가 수정할 수 있는 값을 모두 받는다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=30)
    done: bool

class TaskUpdate(BaseModel):
    """PATCH 요청은 일부 값만 보낼 수 있다."""
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=100)
    owner: str | None = Field(default=None, min_length=1, max_length=30)
    done: bool | None = None


class TaskPublic(BaseModel):
    """클라이언트에 공개하는 작업 응답이다."""

    id: int
    title: str
    owner: str
    done: bool


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id


class DuplicateTaskTitleError(Exception):
    def __init__(self, title: str) -> None:
        self.title = title


# 메모리 저장소이므로 서버를 다시 시작하면 아래 값은 초기화된다.
tasks: dict[int, TaskPublic] = {}
next_task_id = 1


def task_or_404(task_id: int) -> TaskPublic:
    task = tasks.get(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return task


def ensure_unique_title(title: str) -> None:
    normalized = title.casefold()
    for task in tasks.values():
        if task.title.casefold() == normalized:
            raise DuplicateTaskTitleError(title)


@app.exception_handler(TaskNotFoundError)
async def task_not_found_handler(_: Request, error: TaskNotFoundError) -> JSONResponse:
    return JSONResponse(
        status_code=404,
        content={"error": "task_not_found", "message": f"작업 {error.task_id}번이 없다"},
    )


@app.exception_handler(DuplicateTaskTitleError)
async def duplicate_title_handler(_: Request, error: DuplicateTaskTitleError) -> JSONResponse:
    return JSONResponse(
        status_code=409,
        content={"error": "duplicate_title", "message": f"'{error.title}' 제목이 이미 있다"},
    )


@app.get("/tasks", response_model=list[TaskPublic], tags=["tasks"])
def list_tasks() -> list[TaskPublic]:
    return list(tasks.values())


@app.get("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def read_task(task_id: int) -> TaskPublic:
    return task_or_404(task_id)


@app.post(
    "/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(data: TaskCreate) -> TaskPublic:
    global next_task_id

    ensure_unique_title(data.title)
    task = TaskPublic(
        id=next_task_id,
        title=data.title,
        owner=data.owner,
        done=False,
    )
    tasks[task.id] = task
    next_task_id += 1
    return task


# 아래에 PUT, PATCH, DELETE를 차례로 추가하고 매 단계 실행한다.
@app.put("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def replace_task(task_id: int, data: TaskReplace) -> TaskPublic:
    current = task_or_404(task_id)
    ensure_unique_title(data.title)

    replaced = current.model_copy(
        update={"title": data.title, "owner": data.owner, "done": data.done}
    )
    tasks[task_id] = replaced
    return replaced

@app.patch("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def update_task(task_id: int, data: TaskUpdate) -> TaskPublic:
    current = task_or_404(task_id)
    if data.title is not None:
        ensure_unique_title(data.title)

    # exclude_unset=True: 요청에서 생략한 필드 제외
    changes = data.model_dump(exclude_unset=True, exclude_none=True)
    updated = current.model_copy(update=changes)
    tasks[task_id] = updated
    return updated

@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int) -> Response:
    task_or_404(task_id)
    del tasks[task_id]
    return Response(status_code=status.HTTP_204_NO_CONTENT)