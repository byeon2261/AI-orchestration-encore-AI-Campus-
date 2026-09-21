from fastapi import Body, FastAPI, Query, HTTPException, status
from enum import StrEnum
from typing import Annotated


app = FastAPI(title="Book API")

books = [{"id": 1, "title": "어린 왕자"}]

# 기존 `GET /health`, `POST /books`는 동작하게 둔다. 
# 책은 `POST /books`로 등록한 뒤 조회한다.

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
def create_book(title: Annotated[str, Body(embed=True)]) -> dict:
    book = {       
        "id": len(books) + 1,
        "title": title,
    }
    books.append(book)
    return book
