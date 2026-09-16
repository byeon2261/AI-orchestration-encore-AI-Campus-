tasks = ["책 읽기", "과제 하기", "산책하기"]

for index, task in enumerate(tasks, start=1):
    print(f"{index}) 할 일: {task}")

for task in tasks:
    print(f"할 일: {task}")


## 응용 실습
scores = [65, 82, 93, 74]
passed_count = 0

for index, score in enumerate(scores, start=1):
    result = "미판정"
    # TODO: 80점 이상이면 result를 "합격"으로 바꾸고 passed_count를 1 늘린다.
    # TODO: 80점 미만이면 result를 "보충 학습"으로 바꾼다.
    if score >= 80:
        result = "합격"
        passed_count += 1
    else:
        result = "보충 학습"
    print(f"{index}) 점수 {score}: {result}")

print("합격자 수:", passed_count)