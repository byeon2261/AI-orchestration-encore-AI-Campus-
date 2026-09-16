def find_invalid_tasks(tasks):
    """잘못된 작업 항목의 설명을 리스트로 반환한다."""
    invalid_tasks = []
    allowed_statuses = ["완료", "진행 중", "대기"]

    for task in tasks:
        if task["작업 이름"] == "":
            invalid_tasks.append("작업 이름이 비어 있습니다.")

        if task["상태"] not in allowed_statuses:
            invalid_tasks.append(
                "허용되지 않은 상태입니다: " + task["상태"]
            )

    return invalid_tasks
