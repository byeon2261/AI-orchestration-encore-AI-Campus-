"""번호를 붙이고 같은 위치의 두 값을 짝지어 읽는다."""

books = ["파이썬 입문", "자료구조", "알고리즘"]
finished = [True, False, True]

print("번호 목록:")
for number, title in enumerate(books, start=1):
    print(f"{number}. {title}")

print("제목과 완료 여부:")
for title, is_finished in zip(books, finished, strict=True):
    print(title, is_finished)