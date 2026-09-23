# 실습: 상품 목록 페이지 API

JSONPlaceholder 게시글과 Open-Meteo 날씨가 아닌 새로운 상품 도메인을 사용한다. DummyJSON 상품 문서를 읽고 외부 페이지 조건을 우리 API의 입력과 출력 계약으로 바꾼다.

## 만들 파일

- `자기이름/06_async_external_api/product_page_api.py`

완성한 코드 파일 하나를 제출한다.

## 먼저 읽을 외부 문서

[DummyJSON Products 문서](https://dummyjson.com/docs/products)에서 다음 부분을 찾는다.

| 문서에서 찾을 내용 | 코드에서 사용할 위치 |
| --- | --- |
| 상품 목록 엔드포인트 | `https://dummyjson.com/products` |
| `limit` | 한 번에 받을 상품 수 |
| `skip` | 앞에서 건너뛸 상품 수 |
| `select` | 필요한 외부 필드만 요청 |
| 응답의 `products`, `total`, `skip`, `limit` | 외부 응답 모델 |

## 우리 API의 입력 계약

`GET /products`는 다음 쿼리를 받는다.

| 쿼리 | 기본값 | 검증 |
| --- | ---: | --- |
| `page` | 1 | 1 이상 |
| `size` | 10 | 1 이상 20 이하 |

우리 API의 페이지 번호를 외부 API의 위치로 변환한다.

```python
skip = (page - 1) * size
limit = size
```

예를 들어 `page=3&size=10`이면 앞의 20개를 건너뛰고 10개를 요청한다.

## 외부 요청 계약

DummyJSON에 다음 쿼리를 전달한다.

| 외부 쿼리 | 값 |
| --- | --- |
| `limit` | 검증을 통과한 `size` |
| `skip` | `(page - 1) * size` |
| `select` | `id,title,price,category` |

외부 응답의 각 상품은 `id`, `title`, `price`, `category`를 검사한다. 목록을 감싸는 `products`, `total`, `skip`, `limit`도 검사한다.

## 공개 응답 계약

```json
{
  "page": 1,
  "size": 10,
  "total": 194,
  "has_next": true,
  "items": [
    {
      "id": 1,
      "name": "상품 이름",
      "price": 9.99,
      "category": "beauty"
    }
  ]
}
```

- 외부 `title`은 우리 응답의 `name`으로 바꾼다.
- `has_next`는 `skip + 현재 상품 수 < total`이면 `true`다.
- 외부 응답의 이미지, 리뷰, 내부 메타데이터는 공개하지 않는다.

## 외부 실패 처리

| 실패 | 우리 API 응답 |
| --- | --- |
| `page` 또는 `size` 검증 실패 | `422` |
| 외부 API 타임아웃 | `504` |
| 연결 실패·외부 오류 상태 | `502` |
| 예상한 JSON 구조가 아님 | `502` |

`httpx.AsyncClient`는 의존성 함수가 준비한다. 외부 API 호출과 응답 변환은 별도의 `async def` 함수로 분리한다.

## 실행과 확인

```powershell
uv run fastapi dev 06_async_external_api/product_page_api.py
```

| 확인할 요청 | 예상 결과 |
| --- | --- |
| `GET /products` | 첫 페이지 상품 10개를 반환한다. |
| `GET /products?page=2&size=5` | 외부 API에 `skip=5`, `limit=5`를 전달한다. |
| `GET /products?page=0` | 입력 검증에서 `422`가 된다. |
| `GET /products?size=21` | 입력 검증에서 `422`가 된다. |

공개 API는 수업 네트워크 상태에 따라 응답이 늦거나 실패할 수 있다. 이 상황을 코드 오류와 구분한다.

## 구현 확인

- 문서에서 엔드포인트와 쿼리의 의미를 직접 확인했는가?
- `page`와 `size`를 `skip`과 `limit`로 정확히 변환했는가?
- `client.get()`을 `await`했는가?
- 외부 상태 코드와 JSON 구조를 모두 확인했는가?
- 외부 필드명과 우리 공개 필드명을 분리했는가?
- `502`와 `504`를 구분했는가?
- 응답 모델에 없는 외부 필드가 공개되지 않는가?

## 선택: 오류가 발생했을 때 AI로 원인 확인

상품 API가 예상대로 동작했다면 이 활동은 건너뛴다. 오류를 일부러 만들지 않고, 구현 중 실제 오류가 발생했을 때만 AI를 원인 분석에 활용한다.

AI에 질문하기 전에 다음 근거를 준비한다.

- 실행한 HTTP 메서드와 경로
- 기대한 상태 코드와 응답
- 실제 상태 코드와 응답
- 터미널에 표시된 Traceback
- 오류와 직접 관련된 함수

비밀값, 인증 헤더, 내부 주소, 개인정보는 제거한 뒤 다음 형식으로 요청할 수 있다.

```text
다음 FastAPI 외부 API 호출 오류를 분석해 줘.

실행한 요청: [HTTP 메서드와 경로]
기대한 결과: [상태 코드와 응답]
실제 결과: [상태 코드와 응답]
Traceback: [비밀값을 제거한 오류]
관련 코드: [오류와 직접 관련된 함수]

관찰된 사실과 추정을 구분하고, 입력 검증·외부 요청·외부 응답 검증 중
어느 단계에서 실패했는지 설명해 줘. 전체 코드를 다시 작성하지 말고
가장 작은 수정과 수정 뒤 다시 확인할 요청을 제시해 줘.
```

AI의 설명이 실제 상태 코드와 Traceback에 맞는지 확인한 뒤 최소 수정만 적용한다. 실패했던 요청과 기존 정상 요청을 모두 다시 실행한다.