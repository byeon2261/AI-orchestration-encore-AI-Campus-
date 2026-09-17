TASKS = {1: "책 정리", 2: "메일 확인"}


def read_task(raw_task_id: str) -> str:
    task_id = int(raw_task_id)
    return TASKS[task_id]


def main() -> None:
    for raw_task_id in ["1", "unknown", "2", "99"]:
        try:
            title = read_task(raw_task_id)
        except ValueError as error:
            print(f"{raw_task_id!r} 번호 변환 실패: {error}")
        except KeyError as error:
            print(f"{raw_task_id!r} 없는 작업 번호: {error}")
        else:
            print(f"{raw_task_id}: {title}")


if __name__ == "__main__":
    main()