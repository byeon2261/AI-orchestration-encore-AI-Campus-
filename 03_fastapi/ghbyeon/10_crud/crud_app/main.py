
from typing import Annotated

from fastapi import Depends, FastAPI, Request, Response, status
from fastapi.responses import JSONResponse

from .models import TaskCreate, TaskPublic, TaskReplace, TaskUpdate
from .repository import InMemoryTaskRepository
from .service import DuplicateTaskTitleError, TaskNotFoundError, TaskService

app = FastAPI(title="Task CRUD API", version="0.1.0")
repository = InMemoryTaskRepository()
service = TaskService(repository)


def get_task_service() -> TaskService:
    return service


# Annotated와 Depends를 묶은 별칭으로 경로 함수의 의존성을 짧게 표현한다.
Service = Annotated[TaskService, Depends(get_task_service)]


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
def list_tasks(task_service: Service) -> list[TaskPublic]:
    return task_service.list_tasks()


@app.get("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def read_task(task_id: int, task_service: Service) -> TaskPublic:
    return task_service.get_task(task_id)


@app.post(
    "/tasks",
    response_model=TaskPublic,
    status_code=status.HTTP_201_CREATED,
    tags=["tasks"],
)
def create_task(data: TaskCreate, task_service: Service) -> TaskPublic:
    return task_service.create_task(data)


@app.put("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def replace_task(task_id: int, data: TaskReplace, task_service: Service) -> TaskPublic:
    """사용자가 관리하는 작업 필드를 모두 교체한다."""

    return task_service.replace_task(task_id, data)


@app.patch("/tasks/{task_id}", response_model=TaskPublic, tags=["tasks"])
def update_task(task_id: int, data: TaskUpdate, task_service: Service) -> TaskPublic:
    """요청 본문에 들어온 작업 필드만 수정한다."""

    return task_service.update_task(task_id, data)


@app.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["tasks"])
def delete_task(task_id: int, task_service: Service) -> Response:
    task_service.delete_task(task_id)
    # 204 응답은 성공 상태만 전달하며 본문을 보내지 않는다.
    return Response(status_code=status.HTTP_204_NO_CONTENT)