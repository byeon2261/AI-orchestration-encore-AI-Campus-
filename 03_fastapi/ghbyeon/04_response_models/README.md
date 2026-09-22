# 실습: 도서 API 공개 응답

앞서 작성한 `03_pydantic_validation/books_validation_app.py`를 새 파일로 복사하고, 등록 입력과 공개 응답을 분리한다.

## 만들 파일

- `자기이름/04_response_models/books_response_app.py`

## 요구사항

내부 도서 기록에는 기존 필드와 연습용 `internal_note`를 저장한다. 클라이언트에게는 다음 모델의 필드만 반환한다.

| 응답 모델 | 필드 | 적용할 요청 |
| --- | --- | --- |
| `BookPublic` | `id`, `title`, `author`, `pages`, `available` | `POST /books`, `GET /books/{book_id}` |
| `BookSummary` | `id`, `title`, `available` | `GET /books`의 각 항목 |
| `BookList` | `items: list[BookSummary]`, `total: int` | `GET /books` |

`BookCreate`의 입력 검증, 제목 검색, `offset`·`limit`, 없는 번호의 `404`는 그대로 사용한다. `POST /books`는 새 번호를 저장하고 `201`을 반환한다.

## 실행과 확인

자기 이름 폴더의 기존 `uv` 환경에서 실행한다.

```powershell
uv run fastapi dev 04_response_models/books_response_app.py
```

`/docs`에서 책 한 권을 등록하고 생성·상세·목록 응답을 비교한다. `tags`와 `internal_note`가 공개 응답에 없는지, 목록의 각 항목에는 `author`와 `pages`도 없는지 확인한다. 잘못된 본문의 `422`와 없는 번호의 `404`도 확인한다.

제출 파일은 `books_response_app.py` 하나다. `.venv`는 Git에 올리지 않는다.