# 실습: 도서 목록 검색과 페이지 나누기

앞서 만든 도서 목록 API를 별도 파일에 복사하고, 경로·쿼리 매개변수를 추가한다. 같은 `uv` 환경을 사용한다.

## 만들 파일

- `자기이름/02_path_query/books_query_app.py`

## 요구사항

기존 `GET /health`, `POST /books`는 동작하게 둔다. 책은 `POST /books`로 등록한 뒤 조회한다.

| 요청 | 구현할 동작 |
| --- | --- |
| `GET /books/{book_id}` | `book_id`는 1 이상의 정수다. 없는 번호는 `404`, 정수로 바꿀 수 없거나 1 미만이면 `422`다. |
| `GET /books`의 `keyword` | 선택적인 제목 검색어다. 대소문자를 구분하지 않는다. 조건에 맞는 책이 없으면 빈 목록과 `total: 0`을 반환한다. |
| `GET /books`의 `offset` | 기본값 0이다. 0 이상만 허용하고, 검색 결과에서 앞의 `offset`권을 건너뛴다. |
| `GET /books`의 `limit` | 기본값 10이다. 1 이상 20 이하만 허용하고, 건너뛴 뒤 최대 `limit`권을 반환한다. |

`total`은 **검색에 맞는 전체 개수**다. `offset`과 `limit`을 적용한 뒤 실제로 돌려주는 책은 `items`에 담는다.

## 실행과 확인

자기 이름 폴더에서 실행한다.

```powershell
uv run fastapi dev 02_path_query/books_query_app.py
```

`/docs`에서 제목이 다른 책 세 권을 등록한다. `GET /books/1`, `/books/99`, `/books/abc`, `?keyword=파이썬`, `?keyword=없는제목`, `?offset=1&limit=1`, `?limit=0`을 요청해 상태 코드와 응답을 확인한다.

제출 파일은 `books_query_app.py` 하나다. `.venv`는 Git에 올리지 않는다.