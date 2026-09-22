from fastapi import Body, FastAPI, Query, HTTPException, status
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Book API")

books = [{"id": 1, "title": "어린 왕자"}]

#`POST /books`는 다음 JSON 필드를 `BookCreate` 모델로 받는다. 
# 정상 등록은 `201`이며 새 `id`와 `available: true`를 붙여 저장한다.
# | 필드 | 규칙 |
# | --- | --- |
# | `title` | 필수 문자열. 앞뒤 공백을 제거한 뒤 2~80자다. |
# | `author` | 필수 문자열. 앞뒤 공백을 제거한 뒤 2~40자다. |
# | `pages` | 필수 정수. 1~2000이다. |
# | `tags` | 생략하면 빈 목록이다. 입력은 최대 5개이며, 빈 태그를 빼고 공백·대소문자·중복을 정리한다. |
class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=80)
    author: str = Field(min_length=2, max_length=40)
    pages: int = Field(le=1, ge=2000)
    tags: list[str] = Field(default_factory=list, max_length=5)

    @field_validator("tags")
    def normalize_tags(tags: list[str]) -> list[str]:
        normalized: list[str] = []
        for tag in tags:
            cleaned = tag.strip().casefold()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized



@app.get("/health")
def get_health() -> dict[str, str]:
    """서버가 요청을 받을 수 있는지 확인한다."""
    return {"status": "ok"}


@app.get("/books")
def list_books(
    keyword: Annotated[str | None, Query(description="제목 탐색기")] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=0, le=20)] = 10,
) -> dict:
    matched = [
        book
        for book in books
        if keyword is None or keyword.casefold() in book["title"].casefold()
    ]

    total = len(matched)
    items = matched[offset: offset + limit]
    
    return {"keyword":keyword, "items":items, "total": total}

@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
    if book_id < 1:
        raise HTTPException(
            status_code=422, 
            detail="1이상의 정수를 입력해주세요."
        )
    # book = next(book for book in books if books [id] == book_id)
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="book not found"
    )

@app.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: BookCreate) -> dict:
    return {id: 1, **book.model_dump()}