from typing import Annotated

from fastapi import FastAPI, Query, HTTPException

app = FastAPI(title="Query Parameter Variations")

TASKS = [
    {"id": 1, "title": "API 요청 보내기"},
    {"id": 2, "title": "HTTP 응답 읽기"},
    {"id": 3, "title": "API 문서 확인하기"},
    {"id": 4, "title": "오류 로그 살펴보기"},
]

# get 'tasks' 요청시 keyword:str, limit:int 쿼리 매개변수 전달
@app.get("/tasks")
def list_tasks(
    keyword: Annotated[str | None, Query(description="제목에서 찾을 문자열")] = None,
    limit: Annotated[int, Query(ge=1, le=5)] = 3,
) -> dict:
    matched = (
        TASKS
        if keyword is None
        else [task for task in TASKS if keyword.casefold() in task["title"].casefold()]
    )
    return {"keyword": keyword, "items": matched[:limit], "total": len(matched)}

# GET '/search' 요청 시 keyword:str 쿼리 매개변수 전달
# 단, 검색어는 반드시 전달 되어야 함(min_length=2 설정으로 처리)
@app.get("/search")
def search_tasks(
    keyword: Annotated[str, Query(min_length=2)],
) -> dict:
    """반드시 보내야 하는 검색어를 읽는다."""
    matched = [task for task in TASKS if keyword.casefold() in task["title"].casefold()]
    return {"keyword": keyword, "items": matched, "total": len(matched)}

@app.get("/options")
def read_options(verbose: bool = False) -> dict:
    return {"verbose": verbose}