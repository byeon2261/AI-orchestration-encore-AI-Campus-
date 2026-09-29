"""메모리에서 작업 데이터를 관리하는 저장소다."""

from .models import TaskCreate, TaskPublic, TaskReplace, TaskUpdate


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self.clear()

    def clear(self) -> None:
        # _**NAME**: '내부에서만 사용할 객체' 표시
        self._tasks: dict[int, TaskPublic] = {}
        self._next_id = 1

    def list(self) -> list[TaskPublic]:
        return list(self._tasks.values())

    def get(self, task_id: int) -> TaskPublic | None:
        return self._tasks.get(task_id)

    def create(self, data: TaskCreate) -> TaskPublic:
        task = TaskPublic(
            id=self._next_id,
            title=data.title,
            owner=data.owner,
            done=False,
        )
        self._tasks[task.id] = task
        self._next_id += 1
        return task

    def replace(self, task_id: int, data: TaskReplace) -> TaskPublic | None:
        current = self.get(task_id)
        if current is None:
            return None

        # PUT은 사용자가 관리하는 필드를 모두 바꾸고 서버가 만든 값은 유지한다.
        replaced = current.model_copy(
            update={"title": data.title, "owner": data.owner, "done": data.done}
        )
        self._tasks[task_id] = replaced
        return replaced

    def update(self, task_id: int, data: TaskUpdate) -> TaskPublic | None:
        current = self.get(task_id)
        if current is None:
            return None
        # exclude_unset=True는 요청에서 생략한 필드를 변경 대상에서 제외한다.
        changes = data.model_dump(exclude_unset=True, exclude_none=True)
        updated = current.model_copy(update=changes)
        self._tasks[task_id] = updated
        return updated

    def delete(self, task_id: int) -> bool:
        return self._tasks.pop(task_id, None) is not None