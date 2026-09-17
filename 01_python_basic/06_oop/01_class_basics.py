class Book:
    def __init__(self, title: str, author: str) -> None:
        self.title = title
        self.author = author

    def summary(self) -> str:
        return f"{self.title} - {self.author}"


first_book = Book("파이썬 첫걸음", "김하늘")
second_book = Book(title="작은 서비스 만들기", author="이도윤")

print(first_book.summary())
print(second_book.summary())

first_book.title = "수정"
print(first_book.summary())
print(second_book.summary())