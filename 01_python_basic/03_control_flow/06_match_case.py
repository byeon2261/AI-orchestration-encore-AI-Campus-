status = input("작업 실행 상태를 입력하세요 (success/failed/pending): ")

match status:
    case "success":
        message = "완료"
    case "failed":
        message = "실패: 원인 확인"
    case "pending":
        message = "대기 중"
    case _:
        message = "알 수 없는 상태"

print("1) 입력한 상태:", status)
print("2) 안내:", message)

## 응용 실습

statuses = ["success", "timeout", "pending", "unknown", "failed"]

for index, status in enumerate(statuses, start=1):
    message = "미분류"
    match status:
        case "success":
            message = "완료"
        case "failed" | "timeout":
            message = "확인 필요"
        case "pending":
            message = "대기 중"
        case _:
            message = "알 수 없는 상태"

    print(f"{index}) {status}: {message}")