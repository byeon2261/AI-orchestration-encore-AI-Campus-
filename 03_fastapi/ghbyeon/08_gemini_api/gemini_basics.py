
from os import getenv

from google import genai
from google.genai import types

def require_environment(name: str) -> str:
    """필수 환경 변수가 없을 때 호출전에 분명한 오류를 만든다."""
    value= getenv(name)
    if value is None or not value.strip():
        raise RuntimeError(f"{name} 환경 변수를 설정해야 한다.")
    return value

def main() -> None:
    api_key = require_environment("GEMINI_API_KEY")
    model = require_environment("GEMINI_MODEL")

    # Client는 인증 정보와 HTTP 연결을 관리한다.
    # with에서 Client가 오픈이되고 로직이 끝나면 close된다.
    # client 객체로 불린다.
    with genai.Client(api_key=api_key) as client:
        #
        response = client.models.generate_content(
            model=model,
            contents="FastAPI에서 응답 모델을 사용하는 이유를 세 문장으로 설명해 줘.",
            config=types.GenerateContentConfig(
                automatic_function_calling=types.AutomaticFunctionCallingConfig(
                    disable=True
                )
            )
        )

    #후보 응답의 텍스트를 편리하게 꺼내는 속성이다.
    print(response.text)

    # model_version: 서버가 실제응답 생성에 사용한 모델 버젼이 들어올 수 있다.
    print(f"사용 모델: {response.model_version or model}")

    #usage_metadata: 입력/출력/전체 토큰 수를 각각 확인할 수 있다.
    if response.usage_metadata is not None:
        print(f"입력 토근:{response.usage_metadata.prompt_token_count}")
        print(f"출력 토근:{response.usage_metadata.candidates_token_count}")
        print(f"생각 토근:{response.usage_metadata.thoughts_token_count or 0}")
        print(f"전체 토근:{response.usage_metadata.total_token_count}")

if __name__ == "__main__":
    main()