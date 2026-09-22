# 실습: 도서 API의 공통 조회 조건

앞서 작성한 `04_response_models/books_response_app.py`를 새 파일로 복사한다. 요청 검증과 응답 모델은 유지하고, 두 목록 경로가 함께 사용할 조회 조건을 의존성으로 분리한다.

## 만들 파일

- `자기이름/05_dependency_injection/books_dependency_app.py`

## 요구사항

`BookFilters`는 `keyword`, `offset`, `limit`을 담는다. `get_book_filters`는 세 쿼리를 다음 규칙으로 검사하고 `BookFilters` 객체를 반환한다.

| 쿼리 | 규칙 | 생략하면 |
| --- | --- | --- |
| `keyword` | 선택적인 제목 검색어 | `None` |
| `offset` | 0 이상의 정수 | 0 |
| `limit` | 1 이상 20 이하의 정수 | 10 |

다음 두 목록 경로가 모두 `Depends(get_book_filters)`를 사용하게 한다.

| 요청 | 구현할 동작 |
| --- | --- |
| `GET /books` | 전체 도서에서 제목 검색과 목록 범위를 적용한다. |
| `GET /authors/{author_name}/books` | 저자 이름이 일치하는 도서에서 같은 제목 검색과 목록 범위를 적용한다. |

공통 선택 함수는 `BookFilters`를 받고, 저자 이름은 필요할 때만 추가로 받는다. 기존 `BookCreate`, 응답 모델, `POST /books`, `GET /books/{book_id}`와 내부 필드 제외 동작은 유지한다.

## 실행과 확인

```powershell
uv run fastapi dev 05_dependency_injection/books_dependency_app.py
```

`/docs`에서 저자가 다른 책을 세 권 등록한 뒤 다음 요청을 확인한다.

| 확인할 요청 | 예상 결과 |
| --- | --- |
| `GET /books?keyword=파이썬&limit=1` | 제목이 맞는 책을 최대 한 권 반환한다. |
| `GET /authors/김선생/books` | 저자 이름이 일치하는 책만 반환한다. |
| `GET /authors/김선생/books?keyword=FastAPI` | 저자와 제목 조건이 모두 맞는 책만 반환한다. |
| `GET /books?limit=0` | 쿼리 검증 실패로 `422`가 된다. |
| 두 목록 경로의 `/docs` | 같은 `keyword`, `offset`, `limit`이 보인다. |

`Depends(get_book_filters())`처럼 의존성 함수를 미리 호출하지 않았는지 확인한다.

## 다음 실습

도서 API 확인을 마친 뒤 [AI와 함께 카페 주문 API 완성하기](./vibe_coding_order_guide.md)를 진행한다. 종합 실습의 요구사항 정리, AI 요청, 실행 검증, 수정 과정은 별도 문서에서 안내한다.