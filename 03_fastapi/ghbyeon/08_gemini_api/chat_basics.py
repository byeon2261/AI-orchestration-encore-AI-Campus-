"""같은 후속 질문으로 단일 요청과 다중 대화의 문맥 차이를 확인한다."""

from os import getenv

from google import genai
from google.genai import types

from gemini_basics import require_environment


REQUEST_A = "내 학습 주제는 FastAPI 비동기 처리야."
REQUEST_B = "방금 말한 학습 주제로 확인 문제를 하나 만들어 줘."

# 답변을 짧게 제한하면 두 결과의 문맥 차이를 바로 비교할 수 있다.
GENERATION_CONFIG = types.GenerateContentConfig(
    system_instruction=(
        "현재 대화 기록만 사용한다. 학습 주제가 없으면 추측하지 말고 "
        "'주제를 알 수 없다'라고 답한다. 답은 한 문장으로 작성한다."
    ),
    max_output_tokens=120,
    thinking_config=types.ThinkingConfig(thinking_level="minimal"),
    # 이 예제는 Python 함수를 도구로 사용하지 않으므로 AFC를 끈다.
    automatic_function_calling=types.AutomaticFunctionCallingConfig(disable=True),
)


def main() -> None:
    api_key = require_environment("GEMINI_API_KEY")
    model = require_environment("GEMINI_MODEL")

    with genai.Client(api_key=api_key) as client:
        # 두 번의 독립 호출은 앞선 요청과 응답을 다음 호출에 전달하지 않는다.
        single_a = client.models.generate_content(
            model=model,
            contents=REQUEST_A,
            config=GENERATION_CONFIG,
        )
        single_b = client.models.generate_content(
            model=model,
            contents=REQUEST_B,
            config=GENERATION_CONFIG,
        )

        # 같은 chat은 요청 A와 응답 A를 요청 B의 문맥으로 함께 전달한다.
        chat = client.chats.create(model=model, config=GENERATION_CONFIG)
        chat_a = chat.send_message(REQUEST_A)
        chat_b = chat.send_message(REQUEST_B)

    print("[단일 요청: 서로 독립된 두 호출]")
    print(f"요청 A: {REQUEST_A}")
    print(f"응답 A: {single_a.text or '텍스트 응답이 없다'}")
    print(f"요청 B: {REQUEST_B}")
    print(f"응답 B: {single_b.text or '텍스트 응답이 없다'}")

    print("\n[다중 대화: 같은 chat의 두 호출]")
    print(f"요청 A: {REQUEST_A}")
    print(f"응답 A: {chat_a.text or '텍스트 응답이 없다'}")
    print(f"요청 B: {REQUEST_B}")
    print(f"응답 B: {chat_b.text or '텍스트 응답이 없다'}")


if __name__ == "__main__":
    main()