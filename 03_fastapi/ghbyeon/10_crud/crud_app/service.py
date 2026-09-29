"""작업 CRUD의 업무 규칙을 적용하는 서비스다."""

from .models import TaskCreate, TaskPublic, TaskReplace, TaskUpdate
from .repository import InMemoryTaskRepository


class TaskNotFoundError(Exception):
    def __init__(self, task_id: int) -> None:
        self.task_id = task_id


class DuplicateTaskTitleError(Exception):
    def __init__(self, title: str) -> None:
        self.title = title


class TaskService:
    def __init__(self, repository: InMemoryTaskRepository) -> None:
        self.repository = repository

    def list_tasks(self) -> list[TaskPublic]:
        return self.repository.list()

    def get_task(self, task_id: int) -> TaskPublic:
        task = self.repository.get(task_id)
        if task is None:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(self, data: TaskCreate) -> TaskPublic:
        self._ensure_unique_title(data.title)
        return self.repository.create(data)

    def replace_task(self, task_id: int, data: TaskReplace) -> TaskPublic:
        # 존재 여부와 제목 중복은 저장 방식과 관계없는 업무 규칙이다.
        self.get_task(task_id)
        self._ensure_unique_title(data.title, excluding_id=task_id)
        replaced = self.repository.replace(task_id, data)
        if replaced is None:
            raise TaskNotFoundError(task_id)
        return replaced

    def update_task(self, task_id: int, data: TaskUpdate) -> TaskPublic:
        self.get_task(task_id)
        if data.title is not None:
            self._ensure_unique_title(data.title, excluding_id=task_id)
        updated = self.repository.update(task_id, data)
        if updated is None:
            raise TaskNotFoundError(task_id)
        return updated

    def delete_task(self, task_id: int) -> None:
        if not self.repository.delete(task_id):
            raise TaskNotFoundError(task_id)

    def _ensure_unique_title(self, title: str, excluding_id: int | None = None) -> None:
        normalized = title.casefold()
        for task in self.repository.list():
            if task.id != excluding_id and task.title.casefold() == normalized:
                raise DuplicateTaskTitleError(title)