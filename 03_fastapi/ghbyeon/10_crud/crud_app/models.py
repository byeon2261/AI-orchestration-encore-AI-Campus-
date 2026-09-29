"""작업 API의 요청과 응답 모델이다."""

from pydantic import BaseModel, ConfigDict, Field


class TaskCreate(BaseModel):
    """POST에서 새 작업을 만들 때 받는 값이다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=30)


class TaskReplace(BaseModel):
    """PUT에서 사용자가 수정할 수 있는 값을 모두 교체할 때 받는 값이다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # PUT은 전체 교체이므로 세 필드를 모두 요청 본문에 보내야 한다.
    title: str = Field(min_length=1, max_length=100)
    owner: str = Field(min_length=1, max_length=30)
    done: bool


class TaskUpdate(BaseModel):
    """PATCH에서 전달한 값만 부분 수정할 때 받는 값이다."""

    model_config = ConfigDict(str_strip_whitespace=True)

    # PATCH에서는 생략한 필드를 기존 값으로 유지하기 위해 모두 선택 사항으로 둔다.
    title: str | None = Field(default=None, min_length=1, max_length=100)
    owner: str | None = Field(default=None, min_length=1, max_length=30)
    done: bool | None = None


class TaskPublic(BaseModel):
    id: int
    title: str
    owner: str
    done: bool