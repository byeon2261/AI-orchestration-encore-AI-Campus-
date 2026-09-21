from fastapi import FastAPI, Body, HTTPException, status
from typing import Annotated


app = FastAPI(title="Books API", version="0.1.0")
books= []



@app.get("/health")
def get_health() -> dict[str, str]:
    """서버가 요청을 받을 수 있는지 확인한다."""
    return {"status": "ok"}


@app.get("/books")
def list_books() -> dict:
    return {
        "items": books,
        "total": len(books)
    }

@app.get("/books/{book_id}")
def get_book(book_id: int) -> dict:
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