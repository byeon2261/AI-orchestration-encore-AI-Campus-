# 실습: 도서 등록 요청 검증

앞서 작성한 `02_path_query/books_query_app.py`를 새 파일로 복사하고 도서 등록 요청에 Pydantic 모델을 적용한다.

## 만들 파일

- `자기이름/03_pydantic_validation/books_validation_app.py`

## 요구사항

`POST /books`는 다음 JSON 필드를 `BookCreate` 모델로 받는다. 정상 등록은 `201`이며 새 `id`와 `available: true`를 붙여 저장한다.

| 필드 | 규칙 |
| --- | --- |
| `title` | 필수 문자열. 앞뒤 공백을 제거한 뒤 2~80자다. |
| `author` | 필수 문자열. 앞뒤 공백을 제거한 뒤 2~40자다. |
| `pages` | 필수 정수. 1~2000이다. |
| `tags` | 생략하면 빈 목록이다. 입력은 최대 5개이며, 빈 태그를 빼고 공백·대소문자·중복을 정리한다. |

기존 `GET /health`, `GET /books`, `GET /books/{book_id}`도 동작하게 둔다.

## 실행과 확인

자기 이름 폴더의 기존 `uv` 환경에서 실행한다.

```powershell
uv run fastapi dev 03_pydantic_validation/books_validation_app.py
```

`/docs`에서 정상 등록, `author` 누락, 공백만 있는 `title`, `pages`의 0·2001, 태그의 대문자·중복·6개 입력을 확인한다. 정상 등록 후 목록·번호 조회도 확인한다.

제출 파일은 `books_validation_app.py` 하나다. `.venv`는 Git에 올리지 않는다.