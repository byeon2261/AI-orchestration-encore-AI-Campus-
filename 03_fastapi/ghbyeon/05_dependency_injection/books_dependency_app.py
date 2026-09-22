"""도서 등록 입력과 공개할 응답 필드를 서로 다른 모델로 다룬다."""

from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

app = FastAPI(title="Book Response Contract API")



class BookCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=2, max_length=80)
    author: str = Field(min_length=2, max_length=40)
    pages: int = Field(ge=1, le=2000)
    tags: list[str] = Field(default_factory=list, max_length=5)

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


# 목록의 각 책은 상세보다 짧게 보여 준다.
class BookSummary(BaseModel):
    id: int
    title: str
    available: bool


# 목록 전체는 items와 total을 가진다. items의 각 항목도 검증된다.
class BookList(BaseModel):
    items: list[BookSummary]
    total: int


# 서버를 재시작하면 새로 등록한 책은 사라진다.
books: list[dict] = []


@app.get("/health")
def read_health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/books", response_model=BookPublic, status_code=status.HTTP_201_CREATED)
def create_book(book_input: BookCreate) -> dict:
    """입력 검증 후 내부 기록을 저장하고 공개 필드만 돌려준다."""
    book = {
        "id": len(books) + 1,
        **book_input.model_dump(),
        "available": True,
        "internal_note": "수업용 내부 메모",
    }
    books.append(book)
    return book

class BookFilters(BaseModel):
    keyword: str | None
    offset: int
    limit: int


def get_book_filters(
    keyword: Annotated[str | None, Query()] = None,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=20)] = 10,
) -> BookFilters:
    return BookFilters(
        keyword=keyword.casefold() if keyword is not None else None,
        offset=offset,
        limit=limit,
    )


def select_books(filters: BookFilters, author_name: str | None = None) -> dict:
    matched = books
    if author_name is not None:
        matched = [book for book in matched if book["author"] == author_name]
    if filters.keyword is not None:
        matched = [
            book
            for book in matched
            if filters.keyword in book["title"].casefold()
        ]
    return {
        "items": matched[filters.offset : filters.offset + filters.limit],
        "total": len(matched),
    }

@app.get("/books", response_model=BookList)
def list_books(
    filters: Annotated[BookFilters, Depends(get_book_filters)],
) -> dict:
    """검색·목록 나누기 뒤 각 항목을 BookSummary로 제한한다."""
    return select_books(filters)


@app.get("/authors/{author_name}/books", response_model=BookList)
def list_author_books(
    author_name: Annotated[str, Path(min_length=2, max_length=40)],
    filters: Annotated[BookFilters, Depends(get_book_filters)],
) -> dict:
    return select_books(filters, author_name)


@app.get("/books/{book_id}", response_model=BookPublic)
def read_book(book_id: Annotated[int, Path(ge=1)]) -> dict:
    """있는 책은 공개 모델로 보여 주고, 없는 번호는 404를 반환한다."""
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="책을 찾을 수 없다")
