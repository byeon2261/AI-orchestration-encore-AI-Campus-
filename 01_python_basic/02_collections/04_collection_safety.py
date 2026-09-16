# 같은 dict 키에 새 값을 대입하면 기존 값이 덮어써진다.
run = {"agent": "검색", "status": "queued"}
run["status"] = "retrying"
print("1) 갱신한 상태:", run["status"])

# get()은 없는 키를 기본값과 함께 안전하게 조회한다.
print("2) 재시도 횟수:", run.get("retry_count", 0))

# 아래 줄은 없는 키를 대괄호로 조회하므로 KeyError가 발생한다.
# print(run["retry_count"])

# discard()는 set에 값이 없어도 오류가 나지 않는다.
tags = {"python", "ai", "orchestration"}
tags.discard("missing")
print("3) discard 뒤 태그 개수:", len(tags))

# 아래 줄은 없는 값을 삭제하므로 KeyError가 발생한다.
# tags.remove("missing")

# 집합 연산은 공통된 권한과 아직 없는 권한을 비교할 때 쓸 수 있다.
required_permissions = {"read", "summarize", "review"}
granted_permissions = {"read", "summarize"}
print("4) 사용 가능한 권한:", required_permissions & granted_permissions)
print("5) 추가로 필요한 권한:", required_permissions - granted_permissions)
#합집합
print("6) 모든 권한:", required_permissions | granted_permissions)