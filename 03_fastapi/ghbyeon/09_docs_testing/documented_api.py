from dataclasses import dataclass
from os import getenv
from typing import Annotated, Literal

from fastapi import Depends, FastAPI, Request, status
from fastapi.responses import JSONResponse
from google import genai
from google.genai import types
from pydantic import BaseModel, ConfigDict, Field


BACKEND_EXPLAINER_SYSTEM_INSTRUCTION = (
    "너는 백엔드 개발을 배우는 학습자를 위한 기술 설명 도우미다. "
    "한국어로 답하고, 먼저 핵심 개념을 설명한 뒤 필요한 경우 짧은 적용 예시를 제시한다. "
    "질문의 범위에서 벗어나지 말고, 확인하지 않은 실행 결과나 API 동작은 단정하지 않는다."
)


class GenerateRequest(BaseModel):
    """클라이언트가 생성 결과에 영향을 주도록 허용한 입력이다."""

    # 확인: 모델 전체 예시는 Swagger UI의 요청 Example Value에 표시된다.
    model_config = ConfigDict(
        str_strip_whitespace=True,
        json_schema_extra={
            "examples": [
                {
                    "prompt": "OpenAPI와 Swagger UI의 관계를 세 문장으로 설명해 줘.",
                    "max_output_tokens": 500,
                    "thinking_level": "minimal",
                }
            ]
        },
    )

    # 확인: 검증 조건과 설명은 Request body의 Schema에 표시된다.
    prompt: str = Field(
        min_length=2,
        max_length=1000,
        description="Gemini에 전달할 공개 가능한 요청",
    )
    max_output_tokens: int = Field(
        default=500,
        ge=32,
        le=2000,
        description="생성할 수 있는 출력 토큰의 상한",
    )
    thinking_level: Literal["minimal", "low", "medium", "high"] = Field(
        default="minimal",
        description="추론 깊이와 응답 시간·토큰 사용량 사이의 균형",
    )


# 확인: 응답 필드의 설명은 Swagger UI 아래쪽 Schemas에 표시된다.
class TokenUsage(BaseModel):
    input_tokens: int = Field(description="입력에 사용한 토큰 수")
    output_tokens: int = Field(description="응답 생성에 사용한 토큰 수")
    thinking_tokens: int = Field(description="내부 추론에 사용한 토큰 수")
    total_tokens: int = Field(description="입력·출력·생각 토큰을 합한 전체 토큰 수")


class GenerateResponse(BaseModel):
    text: str = Field(description="Gemini가 생성한 텍스트")
    model: str = Field(description="호출한 Gemini 모델 ID")
    usage: TokenUsage


class ErrorResponse(BaseModel):
    error: str = Field(description="프로그램에서 구분하는 오류 코드")
    message: str = Field(description="클라이언트에 공개하는 오류 설명")


class HealthResponse(BaseModel):
    status: Literal["ok"] = Field(description="FastAPI 프로세스의 응답 상태")


@dataclass(frozen=True)
class GeminiResult:
    """외부 SDK 응답에서 수업 API가 공개할 값만 남긴다."""

    text: str
    model: str
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    total_tokens: int


class GeminiConfigurationError(Exception):
    pass


class GeminiProviderError(Exception):
    pass


class GoogleGeminiGateway:
    """Google Gen AI SDK를 호출하는 실제 구현이다."""

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        self.model = model

    async def generate(self, request: GenerateRequest) -> GeminiResult:
        try:
            async with genai.Client(api_key=self.api_key).aio as client:
                response = await client.models.generate_content(
                    model=self.model,
                    contents=request.prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=BACKEND_EXPLAINER_SYSTEM_INSTRUCTION,
                        max_output_tokens=request.max_output_tokens,
                        thinking_config=types.ThinkingConfig(
                            thinking_level=request.thinking_level,
                        ),
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            disable=True,
                        ),
                    ),
                )
        except Exception as error:
            raise GeminiProviderError from error

        if response.text is None or not response.text.strip():
            raise GeminiProviderError

        usage = response.usage_metadata
        return GeminiResult(
            text=response.text,
            model=self.model,
            input_tokens=usage.prompt_token_count if usage is not None else 0,
            output_tokens=usage.candidates_token_count if usage is not None else 0,
            thinking_tokens=(usage.thoughts_token_count or 0) if usage is not None else 0,
            total_tokens=usage.total_token_count if usage is not None else 0,
        )


def get_gemini_gateway() -> GoogleGeminiGateway:
    """환경 설정을 확인하고 실제 Gemini 구현을 제공한다."""

    api_key = getenv("GEMINI_API_KEY")
    if api_key is None or not api_key.strip():
        raise GeminiConfigurationError
    model = getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")
    return GoogleGeminiGateway(api_key=api_key, model=model)


Gemini = Annotated[GoogleGeminiGateway, Depends(get_gemini_gateway)]

# 확인: 태그는 관련 엔드포인트를 그룹으로 묶고 설명과 표시 순서를 정한다.
TAGS_METADATA = [
    {
        "name": "AI 생성",
        "description": "검증한 요청을 Gemini에 전달하고 공개 응답으로 변환한다.",
    },
    {
        "name": "운영",
        "description": "외부 API를 호출하지 않고 서버 프로세스 상태를 확인한다.",
    },
]

# 확인: 애플리케이션 정보는 Swagger UI와 ReDoc의 문서 상단에 표시된다.
app = FastAPI(
    title="문서화된 Gemini API",
    summary="Gemini 텍스트 생성 계약을 문서화하고 검증한다",
    description=(
        "검증한 프롬프트를 Gemini에 전달한다. API 키는 서버 환경 변수에서 "
        "읽으며 요청이나 응답에 포함하지 않는다."
    ),
    # 이 값은 OpenAPI 규격 버전이 아니라 현재 애플리케이션의 버전이다.
    version="0.1.0",
    openapi_tags=TAGS_METADATA,
)


# 확인: 문서의 502·503 응답은 실제 예외 처리기의 상태 코드·본문과 일치해야 한다.
@app.exception_handler(GeminiConfigurationError)
async def configuration_error_handler(
    _request: Request,
    _error: GeminiConfigurationError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content=ErrorResponse(
            error="gemini_not_configured",
            message="Gemini API 설정을 확인해야 한다",
        ).model_dump(),
    )


@app.exception_handler(GeminiProviderError)
async def provider_error_handler(
    _request: Request,
    _error: GeminiProviderError,
) -> JSONResponse:
    return JSONResponse(
        status_code=status.HTTP_502_BAD_GATEWAY,
        content=ErrorResponse(
            error="gemini_provider_error",
            message="Gemini 응답을 가져오지 못했다",
        ).model_dump(),
    )


# 확인: 경로 설명, 태그, 정상 응답 예시와 오류 응답이 Responses에 표시된다.
@app.post(
    "/ai/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Gemini 텍스트 생성",
    description="프롬프트와 생성 옵션을 검증한 뒤 텍스트와 토큰 사용량을 반환한다.",
    response_description="생성된 텍스트와 사용한 모델·토큰 정보",
    tags=["AI 생성"],
    responses={
        # 이 예시는 문서에만 표시되며 실제 Gemini 응답을 고정하지 않는다.
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "text": "OpenAPI는 API의 요청과 응답 계약을 표현한다.",
                        "model": "gemini-3.5-flash-lite",
                        "usage": {
                            "input_tokens": 18,
                            "output_tokens": 64,
                            "thinking_tokens": 20,
                            "total_tokens": 102,
                        },
                    }
                }
            }
        },
        502: {
            "model": ErrorResponse,
            "description": "Gemini 호출 또는 응답 처리 실패",
        },
        503: {
            "model": ErrorResponse,
            "description": "Gemini API 설정 누락",
        },
    },
)
async def generate_text(data: GenerateRequest, gemini: Gemini) -> GenerateResponse:
    result = await gemini.generate(data)
    return GenerateResponse(
        text=result.text,
        model=result.model,
        usage=TokenUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            thinking_tokens=result.thinking_tokens,
            total_tokens=result.total_tokens,
        ),
    )


# 확인: /health는 Gemini를 호출하지 않고 FastAPI 프로세스의 응답만 확인한다.
@app.get(
    "/health",
    response_model=HealthResponse,
    summary="서비스 상태 확인",
    response_description="FastAPI 프로세스의 응답 상태",
    tags=["운영"],
)
def read_health() -> HealthResponse:
    """외부 Gemini 호출 없이 FastAPI 프로세스가 응답하는지 확인한다."""
    return HealthResponse(status="ok")