"""작업 상태가 허용되는지 확인한다"""

def check_status(status: str) -> str:
    if status in ["완료", "진행 중", "대기"]:
        return "정상"
    return "잘못된 상태"


if __name__ == "__main__":
    for status in ["완료", "진행 중", "멈춤"]:
        print(status, check_status(status))
