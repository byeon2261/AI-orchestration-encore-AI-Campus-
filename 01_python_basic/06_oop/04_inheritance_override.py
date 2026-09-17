class Notice:
    def __init__(self, message: str) -> None:
        self.message = message

    def summary(self) -> str:
        return f"안내: {self.message}"


class UrgentNotice(Notice):
    # Override
    def summary(self) -> str:
        return f"긴급: {self.message}"


notices: list[Notice] = [
    Notice("도서관은 6시에 닫는다"),
    UrgentNotice("출입문을 확인한다"),
]
print(notices)
for notice in notices:
    print(notice.summary())