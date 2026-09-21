from fastapi import FastAPI

#title, version은 자동 API 문서 (/dpcs)에도 표시된다.
app = FastAPI(title="Course Task API", version="0.1.0")

#데코레이터 'get/health' 요청을 바로 아래 함수에 연걸한다.
#함수 이름은 자유롭게 정할 수 있지만, 경로와 역할이 드러나게 짓는다.
@app.get("/health")
def read_health() -> dict[str, str]:
    """서버가 요청을 받을 수 있는지 확인한다."""
    #딕셔너리는 Json 응답으로 바뀐다. 기본 상태코드는 200이다.
    return {"status": "ok"}
