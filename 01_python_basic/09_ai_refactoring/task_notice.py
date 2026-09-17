def task_notice(title: str, done: bool, urgent: bool) -> str:
    if done:
        return f"{title}: 완료"
    else:
        if urgent:
            return f"{title}: 먼저 처리"
        else:
            return f"{title}: 대기"


print(task_notice("메일 확인", True, True))
print(task_notice("자료 정리", True, False))
print(task_notice("오류 확인", False, True))
print(task_notice("책상 정리", False, False))