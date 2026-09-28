# 학습 코치 API 

앞서 배운 요청 검증, 비동기 외부 API 호출, 의존성 주입과 오류 처리를 하나의 API로 연결한다. 제출 파일은 `study_coach_api.py` 하나다.

## 필요한 동작

- `POST /study-guides`가 `topic`, `level`, `goal`을 JSON 본문으로 받는다.
- `topic`은 앞뒤 공백을 제거한 뒤 2자 이상 100자 이하만 허용한다.
- `goal`은 앞뒤 공백을 제거한 뒤 2자 이상 300자 이하만 허용한다.
- `level`은 `beginner`, `intermediate`, `advanced` 중 하나만 허용한다.
/- 시스템 프롬프트는 백엔드 개발 학습 코치라는 역할과 `핵심 개념` → `실행 순서` → `확인 문제` 출력 순서를 고정한다.
- `contents`에는 요청마다 달라지는 `topic`, `level`, `goal`만 학습 데이터로 구분해 전달한다.
/- `level`은 서비스가 정한 수준별 설명 기준으로 변환한다. 초급은 용어 풀이, 중급은 개념 관계와 적용 기준, 고급은 장단점과 실패 가능성을 강조한다.
- Gemini 호출 객체는 `Depends`로 엔드포인트에 주입하고, 외부 응답은 `async`로 기다린다.
- 생성 길이는 최대 500토큰, thinking 수준은 `minimal`로 설정하고 AFC는 끈다.
- 정상 응답은 `guide`, `model`과 입력·출력·생각·전체 토큰을 담은 `usage`를 포함한다.
- API 키가 없으면 `503`, Gemini 호출에 실패하면 `502`를 반환한다.

이 과제는 요청마다 독립적으로 응답하는 단일 요청 API다. `chat` 객체나 사용자별 대화 상태는 저장하지 않는다.

시스템 프롬프트에는 서비스가 항상 지킬 역할과 출력 기준을 넣고, 사용자 메시지에는 현재 요청의 데이터만 넣는다. API 키와 같은 비밀 값은 어느 프롬프트에도 포함하지 않는다.

## 실행

`.env`가 있는 자기 프로젝트 루트에서 실행한다.

```powershell
uv run --env-file .env fastapi dev 08_gemini_api/practice/study_coach_api.py
```

서버를 실행한 뒤 `/docs`에서 `POST /study-guides`를 호출한다.

## 확인 요청

```json
{
  "topic": "FastAPI 비동기 외부 API 연동",
  "level": "beginner",
  "goal": "Gemini 호출을 의존성으로 분리하고 오류를 처리하고 싶다"
}
```

정상 응답은 다음 형태다. `guide`의 내용과 토큰 수는 요청마다 달라질 수 있다.

```json
{
  "guide": "생성된 학습 안내",
  "model": "gemini-3.5-flash-lite",
  "usage": {
    "input_tokens": 42,
    "output_tokens": 180,
    "thinking_tokens": 60,
    "total_tokens": 282
  }
}
```

`guide`에 `핵심 개념`, `실행 순서`, `확인 문제`가 순서대로 나타나는지 확인한다. 같은 요청에서 `level`만 `advanced`로 바꿔 용어 풀이 중심의 설명이 장단점과 실패 가능성 중심으로 달라지는지도 비교한다.

## 실패 확인

- `level`을 `expert`로 바꾸면 요청 검증 단계에서 `422`를 반환한다.
- `topic`이나 `goal`을 공백만 보내거나 허용 길이를 벗어나면 `422`를 반환한다.
- API 키가 없는 환경에서 실제 의존성을 사용하면 `503`을 반환한다.
- Gemini 호출이나 응답 처리에 실패하면 `502`를 반환한다.