class Task:
    def __init__(self, title: str) -> None:
        self.title = title
        self.done = False

    def mark_done(self) -> None:
        self.done = True

    def summary(self) -> str:
        status = "완료" if self.done else "진행 중"
        return f"{self.title}: {status}"


class TaskBoard:
    def __init__(self) -> None:
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def completed_count(self) -> int:
        count = 0
        for task in self.tasks:
            if task.done:
                count += 1
        return count


board = TaskBoard()
shopping = Task("장보기")
reading = Task("책 읽기")
board.add_task(shopping)
board.add_task(reading)
shopping.mark_done()

for task in board.tasks:
    print(task.summary())
print("완료:", board.completed_count())