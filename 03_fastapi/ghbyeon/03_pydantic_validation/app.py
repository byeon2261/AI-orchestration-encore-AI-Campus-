from fastapi import FastAPI, status

from pydantic import BaseModel, ConfigDict, Field, field_validator


app= FastAPI(title="Assignment Check Request API")

#BaseModel 을 상속하면 Pydantic이 필드/설정/검증 함수를 읽어 입력 모델을 만든다.
class RunCreate(BaseModel):
    # 설정 딕셔너리를 만든다. model_config는 Pydantic이 읽는 클래스 속성이다.
    # 앞 뒤 공백 제거가 자동으로 설정 된다.
    model_config = ConfigDict(str_strip_whitespace=True)

    # 기본 값이 없는 필드는 필수 값
    agent_name: str = Field(min_length=2, max_length=30, examples=["code-reviewer"])
    prompt: str = Field(min_length=1, max_length=500)
    max_attempts: int = Field(default=3, ge=1, le=5)

    # default_factory=list: tags 값이 넘어오지 않을 경우 빈 리스트로 기본 값 처리
    tags: list[str] = Field(default_factory=list, max_length=5)
    timeout_seconds: int = Field(default=30, ge=1, le=120)

    @field_validator("tags")
    def normalize_tags(tags: list[str]) -> list[str]:
        """빈 태그를 빼고 공백/대소문자/중복을 정리한다."""
        normalized: list[str] = []
        for tag in tags:
            cleaned = tag.strip().casefold()
            if cleaned and cleaned not in normalized:
                normalized.append(cleaned)
        return normalized

@app.post("/runs", status_code=status.HTTP_201_CREATED)
def create_run(
    run: RunCreate
) -> dict:
    """검증을 통과한 요청 값을 확일용 응답으로 돌려준다."""
    # model_dump(): 필드와 기본값을 딕셔너리로 변경.
    return {"id": 1, **run.model_dump()}