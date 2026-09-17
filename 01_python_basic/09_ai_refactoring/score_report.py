def result_message(name: str, score: int) -> str:
    if score >= 80:
        return f"{name}: 통과"
    return f"{name}: 재도전"


def count_passed(scores: list[int]) -> int:
    count = 0
    for score in scores:
        if score >= 80:
            count += 1
    return count


print(result_message("민지", 79))
print(result_message("지우", 80))
print("통과 인원:", count_passed([79, 80, 95]))