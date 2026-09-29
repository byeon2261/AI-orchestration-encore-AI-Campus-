
import pytest
from crud_app.main import app, repository
from fastapi.testclient import TestClient

# 테스트 준비
# TestClient는 실제 서버를 띄우고 네트워크 요청을 보내지는 않지만, 
# FastAPI 내부에서는 실제 HTTP 요청이 들어온 것처럼 요청을 처리하게 해준다.
# fixture는 테스트 함수마다 데이터를 초기화 하고 새로운 TestClient를 만들어준다.
# @pytest.fixture
# def client() -> TestClient:
#     repository.clear()
#     repository._next_id = 1
#     return TestClient(app)
@pytest.fixture
def client() -> TestClient:
    repository.clear()
    app.dependency_overrides.clear()
    return TestClient(app)


# 정상 CRUD 흐름 테스트
# 생성/조회 테스트
# 실행: uv run pytest 파일명 -q -k create_and_read
def test_create_and_read_task(client: TestClient) -> None:
    # Arrange: 요청에 필요한 데이터를 준비한다.
    request_body = {"title": "CRUD 계약 확인", "owner": "홍길동"}

    # Act: 실제 클라이언트처럼 API를 호출한다.
    created = client.post("/tasks", json=request_body)
    found = client.get("/tasks/1")

    # Assert: 상태 코드와 공개 응답을 기대값과 비교한다.
    assert created.status_code == 201
    assert created.json() == {
        "id" : 1,
        "title" : "CRUD 계약 확인",
        "owner" : "홍길동",
        "done" : False
    }
    assert found.status_code == 200
    assert found.json() == created.json()

# PUT 테스트를 추가한 뒤 전체 필드 교체와 422 확인
def test_put_replace_all_editable_fields(client: TestClient) -> None:
    request_body = {"title": "CRUD 계약 확인", "owner": "홍길동"}

    client.post("/tasks", json=request_body)

    replaced = client.put(
        "/tasks/1", 
        json={"title": "CRUD 계약 확인 수정", "owner" : "김길동", "done" : True}
    )

    assert replaced.status_code == 200
    assert replaced.json()["title"] == "CRUD 계약 확인 수정"
    assert replaced.json()["owner"] == "김길동"
    assert replaced.json()["done"] is True
    assert client.put("/tasks/1", json={"owner":"박길동"}).status_code == 422

# PATCH 테스트를 추가한 뒤 요청에서 생략한 필드가 유지되는지 확인
def test_patch_keeps_omitted_fields(client: TestClient) -> None:
    client.post("/tasks", json={"title": "부분 수정", "owner": "홍길동"})

    updated = client.patch("/tasks/1", json={"done": True})

    assert updated.status_code == 200
    assert updated.json()["title"] == "부분 수정"
    assert updated.json()["owner"] == "홍길동"
    assert updated.json()["done"] is True

# DELETE 테스트를 추가한 뒤 빈 204 응답과 이후 404를 확인한다.
def test_delete_returns_empty_204_and_then_404(client: TestClient) -> None:
    client.post("/tasks", json={"title": "삭제 확인", "owner": "홍길동"})

    deleted = client.delete("/tasks/1")

    assert deleted.status_code == 204
    assert deleted.content == b""
    assert client.get("/tasks/1").status_code == 404

# 오류 계약
# 중복 제목 테스트를 추가하고 409 오류 본문을 확인한다.
def test_duplicate_title_returns_409(client: TestClient) -> None:
    client.post("/tasks", json={"title": "중복 확인", "owner": "민지"})

    duplicated = client.post(
        "/tasks",
        json={"title": " 중복 확인 ", "owner": "준호"},
    )

    assert duplicated.status_code == 409
    assert duplicated.json()["error"] == "duplicate_title"

# parametrize는 같은 테스트를 아래 네 개의 method와 body 조합으로 반복한다.
@pytest.mark.parametrize(
    ("method", "body"),
    [
        ("get", None),
        ("put", {"title": "없는 작업", "owner": "민지", "done": False}),
        ("patch", {"done": True}),
        ("delete", None),
    ],
)
def test_missing_task_returns_404(
    client: TestClient,
    method: str,
    body: dict[str, object] | None,
) -> None:
    # getattr(client, "get")은 client.get 메서드를 가져오는 것과 같다.
    request = getattr(client, method)
    response = (
        request("/tasks/999", json=body)
        if body is not None
        else request("/tasks/999")
    )

    assert response.status_code == 404
    assert response.json()["error"] == "task_not_found"
