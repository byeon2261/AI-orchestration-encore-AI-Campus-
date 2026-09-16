# dict는 키와 값을 함께 저장한다.
run = {
    "agent": "검색 에이전트",
    "status": "success",
    "seconds": 1.4,
}

# 새 키에 값을 대입하면 항목이 추가된다.
run["reviewed"] = True
print("1) 에이전트:", run["agent"])
print("2) 실행 정보:", run)

# set은 같은 값을 여러 번 넣어도 하나만 남긴다.
tags = {"python", "ai", "python"}
print("3) 중복 제거 뒤 고유 태그 개수:", len(tags))

# add()로 새 태그를 추가한다.
tags.add("orchestration")
print("4) 추가 뒤 고유 태그 개수:", len(tags))
print("5) orchestration 태그 포함:", "orchestration" in tags)