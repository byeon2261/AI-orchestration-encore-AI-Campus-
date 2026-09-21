from fastapi import FastAPI, Body, HTTPException, status
from typing import Annotated

#title, version은 자동 API 문서 (/dpcs)에도 표시된다.
app = FastAPI(title="Course Task API", version="0.1.0")

# 데이터베이스 대신 python 목록에 할 일을 보관한다.
# id, title, done 속성을 가진 딕셔너리로 관리한다.
tasks = []

#데코레이터 'get/health' 요청을 바로 아래 함수에 연걸한다.
#함수 이름은 자유롭게 정할 수 있지만, 경로와 역할이 드러나게 짓는다.
@app.get("/health")
def read_health() -> dict[str, str]:
    """서버가 요청을 받을 수 있는지 확인한다."""
    #딕셔너리는 Json 응답으로 바뀐다. 기본 상태코드는 200이다.
    return {"status": "ok"}

@app.get("/tasks")
def list_tasks() -> dict:
    """할 일 목록을 반환한다."""
    return {
        "items": tasks,
        "total": len(tasks)
    }

# {task_id}는 경로 매개변수(path parameter)라고 부른다.
@app.get("/tasks/{task_id}")
def get_task(task_id: int) -> dict:
    """주소에 담긴 ID로 할 일을 하나 조회한다."""
    for task in tasks:
        if task["id"] == task_id:
            return task

    #경로는 존재하지만 해당 ID의 데이터가 없으므로 404를 돌려준다.
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, 
        detail="task not found"
    )

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(
    title: Annotated[str, Body(embed=True)]
) -> dict:
    """요청 본문의 title로 할 일을 하나 만든다."""
    # body: title를 http 요청 본문에서 받겠다는 의미
    # emdeb=True: {"title": "..."}의 JSON 형태로 클라이언트가 전송
    task = {
        "id": len(tasks) + 1,
        "title": title,
        "done": False
    }
    tasks.append(task)
    return task