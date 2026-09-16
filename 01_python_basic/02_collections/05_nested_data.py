# dict와 list는 다른 컬렉션을 값으로 포함할 수 있다.
run = {
    "agent": "검색 에이전트",
    "result": {
        "status": "success",
        "sources": ["문서 A", "문서 B"],
    },
}

# 바깥쪽 키부터 안쪽 키 순서로 접근한다.
print("1) 실행한 에이전트:", run["agent"])
print("2) 실행 상태:", run["result"]["status"])

# sources는 list이므로 마지막에는 숫자 인덱스를 사용한다.
print("3) 첫 번째 출처:", run["result"]["sources"][0])