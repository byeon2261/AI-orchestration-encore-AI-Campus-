# 공연 좌석 예약 API 실습

공연 좌석 예약 API에 예외 처리·미들웨어·CORS를 적용한다.

## 작성 파일

자기 실습 디렉터리에 `07_errors_middleware_cors/reservation_api.py`를 작성한다. 제출 파일도 `reservation_api.py` 하나다.

## 요구사항

### 예약 입력과 응답

- 등록 본문은 `guest_name`, `seat_number`를 받는다.
- 두 문자열은 앞뒤 공백을 제거한다.
- 관람객 이름은 2자 이상 30자 이하, 좌석 번호는 2자 이상 5자 이하다.
- 서버는 `id`와 초기 상태 `reserved`를 추가한다.

### 예상 가능한 예외 

- 없는 예약 ID를 조회하면 `ReservationNotFoundError`를 발생시켜 `404`로 변환한다.
- 이미 예약된 좌석을 등록하면 `SeatAlreadyReservedError`를 발생시켜 `409`로 변환한다.
- 오류 본문은 `error`, `message`, `request_id`를 공개한다.
- 한 글자 관람객 이름처럼 입력 검증에 실패하면 FastAPI가 `422`를 반환한다.

### 요청 공통 처리

- 요청의 `X-Request-ID`가 있으면 유지하고 없으면 새 UUID를 만든다.
- 응답에 `X-Request-ID`, `X-Process-Time-Ms`를 추가한다.
- 서버 로그에 요청 ID, 메서드, 경로, 상태 코드, 처리 시간을 기록한다.

### CORS

- `http://127.0.0.1:18080`만 허용한다.
- `GET`, `POST`, `Content-Type`, `X-Request-ID`를 허용한다.
- 브라우저가 두 공통 응답 헤더를 읽을 수 있게 공개한다.

## 실행

`03_fastapi_basics` 디렉터리에서 실행한다.

```powershell
uv run fastapi dev 07_errors_middleware_cors/practice/reservation_api.py
```

## 확인할 요청

| 요청 | 예상 결과 |
| --- | --- |
| `GET /reservations/1` | 기존 예약과 `200` |
| `GET /reservations/99` | `reservation_not_found`와 `404` |
| `A1` 좌석을 다시 `POST /reservations` | `seat_already_reserved`와 `409` |
| 새로운 좌석 등록 | 생성된 예약과 `201` |
| 한 글자 관람객 이름 등록 | 입력 검증 실패와 `422` |

## 브라우저 CORS 확인

상위 디렉터리의 `cors_client.html`을 18080 포트로 제공하고 API 경로 입력을 `/reservations/1`로 바꾼다. 단순 GET과 사용자 정의 헤더 GET을 각각 실행한다. 개발자 도구의 Network에서 두 번째 요청 앞에 OPTIONS가 있는지 확인한다.