# 시작 목록을 확인한다.
agents = ["검색", "분석"]
print("1) 시작 목록:", agents)

# append()는 마지막에 하나를 추가하고 반환값은 None이다.
append_result = agents.append("요약")
print("2) append 반환값:", append_result)
print("3) append 뒤:", agents)

# extend()는 여러 항목을 더하고, insert()는 원하는 위치에 넣는다.
agents.extend(["검증", "보고"])
agents.insert(1, "분배")
print("4) extend와 insert 뒤:", agents)

# pop()은 항목을 꺼내고, remove()는 지정한 값을 삭제한다.
last_agent = agents.pop()
agents.remove("분석")
print("5) pop으로 꺼낸 항목:", last_agent)
print("6) remove 뒤:", agents)

a = [1, 2, 1, 3, 1]
a.remove(1)  # 첫 번째 1만 제거된다.
print("7) remove로 첫 번째 1 제거 뒤:", a)