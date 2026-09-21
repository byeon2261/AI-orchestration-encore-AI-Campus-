import httpx


BASE_URL = "http://127.0.0.1:8000"

CASES = [
    ("전체 목록", {}),
    ("상태·검색어·구간 조합", {"state": "queued", "keyword": "api", "offset": 1, "limit": 1}),
    ("결과가 없는 검색", {"keyword": "없는제목"}),
    ("끝을 지난 구간", {"offset": 99}),
    ("허용 범위 밖", {"limit": 0}),
]

# with 블럭은 IO(입출력) 상황에 사용되는 문법
with httpx.Client(base_url=BASE_URL, timeout=5.0) as client:
    for label, params in CASES:
        response = client.get("/tasks", params=params)
        print(f"{label}: {response.request.url} -> {response.status_code}")
        print(response.json())