class TaskNotFoundError(Exception):
    pass


TASKS = {1: "책 정리"}


def get_task(task_id: int) -> str:
    if task_id not in TASKS:
        raise TaskNotFoundError(f"작업 {task_id}번이 없다")
    return TASKS[task_id]


for task_id in [1, 99]:
    try:
        print(get_task(task_id))
    except TaskNotFoundError as error:
        print(f"조회 실패: {error}")