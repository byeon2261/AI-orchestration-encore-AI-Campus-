"""JSONPlaceholder를 호출해 외부 응답을 내부 공개 계약으로 변경한다."""

from typing import Annotated
from fastapi import FastAPI, Path, Query, HTTPException
from pydantic import BaseModel, ValidationError
import httpx
import asyncio


app = FastAPI(title="JSONPlaceholder Client API")

JSONPLACEHOLDER_URL = "https://jsonplaceholder.typicode.com/posts"

#외부 JSON 구조와 우리 API가 공개할 구조를 서로 다른 모델로 만든다.
class ExternalPost(BaseModel):
    """JSONPlaceholder가 반환해야 하는 게시글 구조이다."""
    userId: int
    id: int
    title: str
    body: str

class PostPublic(BaseModel):
    """우리 API가 클라이언트에게 공개하는 게시글 구조"""
    id: int
    title: str
    preview: str

@app.get("/posts/{post_id}", response_model=PostPublic)
async def read_post(
    post_id: Annotated[int, Path(ge=1, le=100)]
) -> PostPublic:

    try:    
        # asyncClient : 외부 API를 요청할 때 사용하는 비동기 HTTP 도구
        # async with: 클라이언트를 열고, 블록을 벗어날 때 오류 여부와 관계 없이 닫는다.
        # await를 사용하지 않으면 코르티객체를 생성해서 보내준다.
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{JSONPLACEHOLDER_URL}/{post_id}")

        # 4xx, 5xx 외부 응답을 정상 JSON처럼 처리하지 않고 httpx예외롤 변경한다.
        response.raise_for_status()
        # 외부 JSON을 검사한 뒤 우리 API가 공개할 필드만 새 모델로 만든다.
        external = ExternalPost.model_validate(response.json())
        return PostPublic(
            id=external.id,
            title=external.title,
            preview=external.body[:60]
        )


    except httpx.TimeoutException as error:
        raise HTTPException(status_code=504, detail="외부 API 응답 시간이 초과했습니다.") from error
    except (httpx.HTTPError, ValidationError, ValueError) as error:
        raise HTTPException(status_code=502, detail="외부 API 응답을 처리되지 않습니다.") from error