"""예외 API를 확장해 요청 로깅 미들웨어와 CORS를 적용한다."""


import logging
from time import perf_counter
from uuid import uuid4

from typing import Literal

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

# CORS를 적용할 때 추가한다.
from fastapi.middleware.cors import CORSMiddleware


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id


class TaskTitleConflictError(Exception):
    def __init__(self, title: str) -> None:
        self.title = title


class TaskCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=30)


class TaskResponse(BaseModel):
    id: int
    title: str
    status: Literal["todo"]


class ErrorResponse(BaseModel):
    error: str
    message: str
    # 추가. 오류 본문과 서버 로그를 같은 요청 ID로 연결한다.
    request_id: str


# 서버 로그를 출력할 준비 
# logging은 파이썬 표준 로그 도구다. INFO 이상 수준의 로그를 아래 형식으로 출력한다.
# %(levelname)s와 %(name)s는 logging이 로그 수준과 로거 이름으로 채운다.
logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s %(name)s %(message)s",
)

# getLogger()는 이름이 붙은 Logger 객체를 돌려준다.
# 이 이름을 사용하면 어느 코드에서 남긴 로그인지 출력에서 구분할 수 있다.
logger = logging.getLogger("course.resilient_api")

app = FastAPI(title="Resilient Task API")

TASKS: dict[int, dict[str, object]] = {
    1: {"id": 1, "title": "예외 처리 흐름 확인", "status": "todo"},
}


# 오류 응답에도 요청 ID 연결
def make_error_body(
    request: Request,
    error: str,
    message: str,
) -> dict[str, str]:
    """예외 처리기와 미들웨어가 같은 공개 오류 형식을 사용하게 한다."""
    # request.state는 한 요청을 처리하는 동안 값을 공유하는 보관 공간이다.
    # 미들웨어가 먼저 저장한 request_id를 예외 처리기에서도 읽을 수 있다.
    return ErrorResponse(
        error=error,
        message=message,
        request_id=request.state.request_id,
    ).model_dump()


#  _request를 request로 바꾸고 공개 본문만 확장한다.
@app.exception_handler(TaskNotFoundError)
def task_not_found_handler(
    request: Request,
    error: TaskNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=make_error_body(
            request,
            error="task_not_found",
            message=f"작업 {error.task_id}번을 찾을 수 없다",
        ),
    )


@app.exception_handler(TaskTitleConflictError)
def task_title_conflict_handler(
    request: Request,
    error: TaskTitleConflictError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=make_error_body(
            request,
            error="task_title_conflict",
            message=f"'{error.title}' 작업은 이미 등록되어 있다",
        ),
    )


# 모든 HTTP 요청의 앞뒤에서 공통 작업 수행
# @app.middleware("http")는 아래 함수를 HTTP 요청 공통 처리기로 등록한다.
# request는 현재 요청이고, call_next는 요청을 다음 처리 단계로 보내는 함수다.
@app.middleware("http")
async def add_request_context(request: Request, call_next):
    """모든 요청의 앞뒤에서 요청 ID, 처리 시간과 로그를 관리한다."""
    # perf_counter()는 현재 시각이 아니라 짧은 처리 시간을 재는 정밀한 타이머다.
    started_at = perf_counter()

    # 클라이언트가 보낸 ID가 있으면 유지하고, 없으면 uuid4()로 새 고유값을 만든다.
    # HTTP 헤더에는 문자열을 넣어야 하므로 UUID 객체를 str()로 변환한다.
    # uuid4: Generate a random UUID.
    request_id = request.headers.get("X-Request-ID", str(uuid4()))

    request.state.request_id = request_id

    try:
        # call_next(request)가 다음 미들웨어와 경로 함수를 실행한다.
        # await하는 동안 기다린 뒤, 그 단계들이 만든 Response를 돌려받는다.
        response = await call_next(request)
    except Exception:
        # logger.exception()은 메시지와 함께 예외 종류·호출 위치를 서버에 기록한다.
        # 내부 오류 정보는 로그에만 남기고 공개 응답에는 안전한 문구만 넣는다.
        logger.exception(
            "unexpected_error request_id=%s method=%s path=%s",
            request_id,
            request.method,
            request.url.path,
        )
        response = JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content=make_error_body(
                request,
                error="internal_server_error",
                message="서버에서 요청을 처리하지 못했다",
            ),
        )

    # 시작값을 빼서 초 단위 경과 시간을 구하고 1000을 곱해 밀리초로 바꾼다.
    process_time_ms = (perf_counter() - started_at) * 1000
    response.headers["X-Request-ID"] = request_id
    response.headers["X-Process-Time-Ms"] = f"{process_time_ms:.2f}"

    # %s와 %.2f에는 뒤의 값이 순서대로 들어간다. logging이 출력할 때 치환한다.
    logger.info(
        "request_completed request_id=%s method=%s path=%s status=%s process_time_ms=%.2f",
        request_id,
        request.method,
        request.url.path,
        response.status_code,
        process_time_ms,
    )
    return response


@app.get("/tasks/{task_id}", response_model=TaskResponse)
def read_task(task_id: int) -> dict[str, object]:
    task = TASKS.get(task_id)
    if task is None:
        raise TaskNotFoundError(task_id)
    return task


@app.post(
    "/tasks",
    response_model=TaskResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_task(task_create: TaskCreate) -> dict[str, object]:
    normalized_title = task_create.title.casefold()
    if any(str(task["title"]).casefold() == normalized_title for task in TASKS.values()):
        raise TaskTitleConflictError(task_create.title)

    task_id = max(TASKS, default=0) + 1
    task = {"id": task_id, "title": task_create.title, "status": "todo"}
    TASKS[task_id] = task
    return task


# 미들웨어가 예상하지 못한 500 오류도 감싸는지 확인한다.
@app.get("/errors/unexpected", tags=["실패 확인"])
def raise_unexpected_error() -> dict[str, str]:
    """수업에서 예상하지 못한 500 오류 경계를 확인하기 위한 경로다."""
    raise RuntimeError("이 내부 오류 문구는 공개 응답에 포함되면 안 된다")
