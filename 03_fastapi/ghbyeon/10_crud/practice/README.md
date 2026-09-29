# 역할별 CRUD 계약 테스트 

수업에서 완성한 `test_task_api.py`를 참고해 역할별로 분리한 `crud_app`의 공개 계약을 검사한다.

## 작성할 파일

`10_crud/test_crud_app.py`를 작성한다. 제출 파일도 이 파일 하나다.

## 작성 순서

1. `test_task_api.py`의 테스트를 `test_crud_app.py`로 복사한다.
2. `task_api` 대신 `crud_app.main`의 `app`과 `repository`를 가져온다.
3. `client` fixture에서 저장소와 의존성 재정의를 초기화한다.
4. 기존 테스트 함수는 바꾸지 않고 역할별 앱에서도 같은 계약을 확인한다.

fixture는 다음 형태로 작성한다.

```python
@pytest.fixture
def client() -> TestClient:
    repository.clear()
    app.dependency_overrides.clear()
    return TestClient(app)
```

## 실행

```powershell
# 역할별 CRUD 테스트만 실행
uv run pytest 10_crud/test_crud_app.py -q
```

역할별 테스트만 실행했을 때 `9 passed`가 나오면 다음 계약을 모두 통과한 것이다.

- 생성과 단일 조회
- PUT 전체 교체와 필드 누락의 `422`
- PATCH 부분 수정
- DELETE의 빈 `204`
- 중복 제목의 `409`
- 없는 작업의 `404`

`fixture 'client' not found`가 나오면 `@pytest.fixture`와 `client` 함수가 파일 최상위에 있는지 확인한다. import 오류가 나오면 프로젝트 루트에서 명령을 실행했는지 확인한다.