import pytest
from fastapi.testclient import TestClient

import task_api

# 테스트 준비
# TestClient는 실제 서버를 띄우고 네트워크 요청을 보내지는 않지만,
# FastAPI 내부에서는 실제 HTTP 요청이 들어온 것처럼 요청을 처리하게 해준다.
# fixture는 테스트 함수마다 데이터를 초기화하고 새로운TestClient를 만들어준다.
@pytest.fixture
def client() -> TestClient:
    task_api.tasks.clear()
    task_api.next_task_id = 1
    return TestClient(task_api.app)


# 정상 CRUD 흐름 테스트
# 생성/조회 테스트
# 실행: uv run pytest 파일명 -q -k 함수명
# 함수명 <- create_and_read
def test_create_and_read_task(client: TestClient) -> None:
    # Arreange: 요청에 필요한 데이터를 준비한다.
    request_body = {"title": "CRUD 계약 확인", "owner": "홍길동"}

    # Act: 실제 클라이언트처럼 API를 호출한다.
    created = client.post("/tasks", json=request_body)
    found = client.get("/tasl/1")

    # Assert: 상테 코드와 공개 응답을 기대값과 비교한다.
    assert created.status_code == 201
    assert created.json() == {
        "id": 1,
        "title": "CRUD 계약 확인",
        "owner": "홍길동",
        "done": False
    }