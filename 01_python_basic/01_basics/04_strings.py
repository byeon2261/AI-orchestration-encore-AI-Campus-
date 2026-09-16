raw_status = "  Success  "
#strip() 메서드는 문자열의 양쪽 공백을 제거합니다.
#lower() 메서드는 문자열을 소문자로 변환합니다.
normalized_status = raw_status.strip().lower()
message = "검색 에이전트가 문서 12개를 찾았다."

#!r은 눈에 보이지 않는 앞뒤 공백까지 확인할 때 유용하다. 따옴표를 추가해준다.
print(f"원본: {raw_status!r}")
print(f"원본: {raw_status}")
print(f"정리: {normalized_status!r}")
print(f"첫 글자: {message[0]}")
print(f"앞 네 글자: {message[:4]}")
print(f"앞 네 글자: {message[1:4]}")
print(f"요약: {message}")