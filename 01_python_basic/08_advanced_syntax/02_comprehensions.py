"""리스트·집합·딕셔너리 컴프리헨션의 결과를 비교한다."""

reading = [("파이썬 입문", True), ("자료구조", False), ("알고리즘", True)]

pending_with_loop: list[str] = []
for title, is_finished in reading:
    if not is_finished:
        pending_with_loop.append(title)
## 같은 동작이다.
pending_with_comprehension = [
    title for title, is_finished in reading if not is_finished
]

print("반복문:", pending_with_loop)
print("리스트 컴프리헨션:", pending_with_comprehension)

numbers = [1, 2, 2, 3]
selected_numbers = {number for number in numbers if number >= 2}
squares_by_number = {number: number * number for number in numbers}

print("집합 원소 수:", len(selected_numbers))
print("딕셔너리:", squares_by_number)