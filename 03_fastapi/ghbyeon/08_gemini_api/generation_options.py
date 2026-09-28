"""상단의 생성 옵션을 바꾸며 Gemini 응답 차이를 관찰한다."""

from os import getenv
from time import perf_counter

from google import genai
from google.genai import types

from gemini_basics import require_environment


PROMPT = (
    "FastAPI 서버가 외부 API A(3초)와 B(2초)를 동시에 호출하고, "
    "두 결과를 받은 뒤 API C(1초)를 호출한다. 전체 최소 시간과 "
    "async 실행 순서, 실패 처리 지점을 여덟 단계로 자세히 설명해 줘."
)
# 1차 관찰: 80으로 실행한 뒤 300으로 바꾸고 출력 길이와 토큰 수를 비교한다.
MAX_OUTPUT_TOKENS = 500
# 2차 관찰: 같은 질문에서 minimal을 high로 바꾸고 시간과 생각 토큰을 비교한다.
THINKING_LEVEL = "minimal"
# THINKING_LEVEL = "high"


def main() -> None:
    api_key = require_environment("GEMINI_API_KEY")
    model = require_environment("GEMINI_MODEL")

    started_at = perf_counter()
    with genai.Client(api_key=api_key) as client:
        response = client.models.generate_content(
            model=model,
            contents=PROMPT,
            config=types.GenerateContentConfig(
                max_output_tokens=MAX_OUTPUT_TOKENS,
                thinking_config=types.ThinkingConfig(
                    thinking_level=THINKING_LEVEL,
                ),
                # 이 예제는 Python 함수를 도구로 사용하지 않으므로 AFC를 끈다.
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True,
                ),
            ),
        )
    elapsed_seconds = perf_counter() - started_at

    print(f"모델: {response.model_version or model}")
    print(
        f"설정: max_output_tokens={MAX_OUTPUT_TOKENS}, "
        f"thinking_level={THINKING_LEVEL}"
    )
    print(f"응답 시간: {elapsed_seconds:.2f}초")
    print(response.text or "텍스트 응답이 없다")

    usage = response.usage_metadata
    if usage is not None:
        print(f"출력 토큰: {usage.candidates_token_count}")
        print(f"생각 토큰: {usage.thoughts_token_count or 0}")


if __name__ == "__main__":
    main()