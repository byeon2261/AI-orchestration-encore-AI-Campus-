from fastapi import Body, FastAPI, Query, HTTPException, status
from enum import StrEnum
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Book API")

books: dict[int, dict[str, object]] = {
    1: {"id": 1, 
        "title": "어린 왕자", 
        "author": "변건형", 
        "pages": 422, 
        "tags":["classic", "kids"],
        "available": True
    }
}

# 내부 도서 기록에는 기존 필드와 연습용 `internal_note`를 저장한다. 
# 클라이언트에게는 다음 모델의 필드만 반환한다.

# | 응답 모델 | 필드 | 적용할 요청 |
# | --- | --- | --- |
# | `BookPublic` | `id`, `title`, `author`, `pages`, `available` | `POST /books`, `GET /books/{book_id}` |
# | `BookSummary` | `id`, `title`, `available` | `GET /books`의 각 항목 |
# | `BookList` | `items: list[BookSummary]`, `total: int` | `GET /books` |
# `BookCreate`의 입력 검증, 제목 검색, `offset`·`limit`, 없는 번호의 `404`는 그대로 사용한다. 
# `POST /books`는 새 번호를 저장하고 `201`을 반환한다. |

class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=80)
    author: str = Field(min_length=2, max_length=40)
    pages: int = Field(ge=1, le=2000)
    tags: list[str] = Field(default_factory=list, max_length=5)
    available: bool = Field(default=True)

    @field_validator("tags")
    def normalize_tags(tags: list[str]) -> list[str]:
        normalized: list[str] = []
        for tag in tags:
            cleaned = tag.strip().casefold()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

class BookPublic(BaseModel):
    id: int
    title: str
    author: str
    pages: int
    available: bool

class BookSummary(BaseModel):
    id: int
    title: str
    available: bool

class BookList(BaseModel):
    items: list[BookSummary]
    total: int

@app.get("/health")
def get_health() -> dict[str, str]:
    """서버가 요청을 받을 수 있는지 확인한다."""
    return {"status": "ok"}


@app.get("/books", response_model=BookList)
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

@app.get("/books/{book_id}", response_model=BookPublic)
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

@app.post("/books", status_code=status.HTTP_201_CREATED, response_model=BookPublic)
def create_book(book: BookCreate) -> dict:
    book_id = max(books, default=0) + 1
    record: dict[str, object] = {
            "id": book_id,
            **book.model_dump(),
    }
    # books[id] = record
    books.append(book)
    return record