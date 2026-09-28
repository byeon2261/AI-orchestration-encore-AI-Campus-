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


class ReservedNotFoundError(Exception):
    def __init__(self, reserve_id: int) -> None:
        self.reserve_id = reserve_id


class SeatAlreadyReservedError(Exception):
    def __init__(self, seat_number: str) -> None:
        self.seat_number = seat_number


class ReserveCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    guest_name: str = Field(min_length=2, max_length=30)
    seat_number: str = Field(min_length=2, max_length=5)
    reserved: bool


class ReserveResponse(BaseModel):
    id: int
    guest_name: str
    seat_number: str
    reserved: str


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

app = FastAPI(title="Resilient Reserve API")

RESERVES: dict[int, dict[str, object]] = {
    1: {"id": 1, 
        "guest_name" : "변건형",
        "seat_number": "A1",
        "reserved": "True"},
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
@app.exception_handler(ReservedNotFoundError)
def reserve_not_found_handler(
    request: Request,
    error: ReservedNotFoundError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_404_NOT_FOUND,
        content=make_error_body(
            request,
            error="reserve_not_found",
            message=f"예약 {error.reserve_id}을 찾을 수 없다",
        ),
    )


@app.exception_handler(SeatAlreadyReservedError)
def seat_already_reserved_handler(
    request: Request,
    error: SeatAlreadyReservedError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_409_CONFLICT,
        content=make_error_body(
            request,
            error="reserve_seat_number",
            message=f"'{error.seat_number}' 이미 예약된 좌석 입니다",
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


# add_middleware()는 기존 경로함수를 코치지 않고 CORS공통 처리를 앱에 추가한다.
# 브라우져가 보내는 preflight도 CORSMiddlewate가 자동으로 응답한다.
app.add_middleware(
    CORSMiddleware,
    # 이 Origin에서 열린 브라우저 페이지의 교차 출처 요청만 허용한다.
    allow_origins=["http://127.0.0.1:18080"],
    # 쿠키/Authentication 같은 자격증명은 이 예제에서 사용하지 않는다.
    allow_credentials=False,
    # 브라우저가 실제 요청에 사용할 수 있는 HTTP 메서드다.
    allow_methods=["GET", "POST"],
    # 브라우저가 실제 요청에 포함할 수 있는 요청 헤더다.
    allow_headers=["Content-Type", "X-Request-ID"],
    # 브라우저 자밥스크립트가 읽을 수 있도록 공개할 응답 헤더다.
    expose_headers=["X-Request-ID", "X-Process-Time-Ms"]
)



@app.get("/reserves/{reserve_id}", response_model=ReserveResponse)
def read_reserve(reserve_id: int) -> dict[str, object]:
    reserve = RESERVES.get(reserve_id)
    if reserve is None:
        raise ReservedNotFoundError(reserve_id)
    return reserve


@app.post(
    "/reserves",
    response_model=ReserveResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_reserve(reserve_create: ReserveCreate) -> dict[str, object]:
    normalized_seat_number = reserve_create.seat_number.casefold()
    if any(str(reserve["seat_number"]).casefold() == normalized_seat_number for reserve in RESERVES.values()):
        raise seat_already_reserved_handler(reserve_create.seat_number)

    reserve_id = max(RESERVES, default=0) + 1
    reserve = {"id": reserve_id, 
               "seat_number": reserve_create.seat_number, 
               "guest_name": reserve_create.guest_name,
               "reserved": "todo"}
    RESERVES[reserve_id] = reserve
    return reserve


# 미들웨어가 예상하지 못한 500 오류도 감싸는지 확인한다.
@app.get("/errors/unexpected", tags=["실패 확인"])
def raise_unexpected_error() -> dict[str, str]:
    """수업에서 예상하지 못한 500 오류 경계를 확인하기 위한 경로다."""
    raise RuntimeError("이 내부 오류 문구는 공개 응답에 포함되면 안 된다")
