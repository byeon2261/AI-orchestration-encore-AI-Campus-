"""Gemini 호출을 요청·응답 계약과 의존성으로 감싼 FastAPI 예제다."""

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
    "한국어로 답하고, 먼저 핵심 개념을 설명한 뒤 실행 순서를 설명한 뒤 필요한 경우 짧은 확인 문제를 제시한다. "
    "질문의 범위에서 벗어나지 말고, 확인하지 않은 실행 결과나 API 동작은 단정하지 않는다."
)


class GenerateRequest(BaseModel):
    """클라이언트가 생성 결과에 영향을 주도록 허용한 입력이다."""

    # 문자열의 양끝 공백을 제거한 뒤 길이와 값 범위를 검증한다.
    model_config = ConfigDict(str_strip_whitespace=True)

    topic: str = Field(min_length=2, max_length=100)
    goal: str = Field(min_length=2, max_length=300)
    level: Literal["beginner", "intermediate", "advanced"] = "beginner"


class TokenUsage(BaseModel):
    input_tokens: int
    output_tokens: int
    thinking_tokens: int
    total_tokens: int


class GenerateResponse(BaseModel):
    # text: str
    guide: str
    model: str
    usage: TokenUsage


class ErrorResponse(BaseModel):
    error: str
    message: str


# frozen: 한번 지정되면 값이 변경되지 않는다.
@dataclass(frozen=True)
class GeminiResult:
    """외부 SDK 응답에서 수업 API가 공개할 값만 남긴다."""

    text: str
    # guide: str
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
            # aio 클라이언트로 외부 응답을 기다리는 동안 서버가 다른 요청을 처리할 수 있다.
            async with genai.Client(api_key=self.api_key).aio as client:
                response = await client.models.generate_content(
                    model=self.model,
                    contents=request.topic,
                    config=types.GenerateContentConfig(
                        # 시스템 프롬프트는 사용자가 아니라 서비스가 정한 고정 동작이다.
                        system_instruction=BACKEND_EXPLAINER_SYSTEM_INSTRUCTION,
                        # goal=request.goal,
                        thinking_config=types.ThinkingConfig(
                            thinking_level="minimal"
                        ),
                        automatic_function_calling=types.AutomaticFunctionCallingConfig(
                            disable=True,
                        ),
                    ),
                )
        except Exception as error:
            # SDK 내부 정보와 API 키가 HTTP 응답에 노출되지 않도록 업무 예외로 바꾼다.
            raise GeminiProviderError from error

        # if response.text is None or not response.text.strip():
        if response.text is None or not response.text.strip():
            raise GeminiProviderError

        usage = response.usage_metadata
        # SDK 응답을 FastAPI가 사용할 내부 결과로 변환한다.
        return GeminiResult(
            text=response.text,
            # guide=response.guide,
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


# 엔드포인트는 실제 Gemini 호출 객체를 의존성으로 전달받는다.
Gemini = Annotated[GoogleGeminiGateway, Depends(get_gemini_gateway)]

app = FastAPI()


# 설정 누락과 외부 공급자 실패를 서로 다른 HTTP 상태로 변환한다.
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


@app.post("/study-guides", response_model=GenerateResponse)
async def generate_text(data: GenerateRequest, gemini: Gemini) -> GenerateResponse:
    # 엔드포인트는 공급자를 직접 호출하지 않고 주입받은 객체에 요청을 맡긴다.
    result = await gemini.generate(data)
    return GenerateResponse(
        guide=result.text,
        # text=result.text,
        model=result.model,
        usage=TokenUsage(
            input_tokens=result.input_tokens,
            output_tokens=result.output_tokens,
            thinking_tokens=result.thinking_tokens,
            total_tokens=result.total_tokens,
        ),
    )