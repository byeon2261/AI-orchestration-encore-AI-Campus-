tasks = []

while True:
    task = input("할 일을 입력하세요. 끝내려면 끝: ")

    if task == "끝":
        print("1) 입력 종료: 더 이상 할 일을 받지 않는다.")
        break

    if task == "":
        print("2) 빈 입력: 이번 입력은 건너뛴다.")
        continue

    tasks.append(task)
    print(f"3) 기록한 할 일 {len(tasks)}: {task}")

print("4) 기록한 할 일 수:", len(tasks))
print("5) 기록한 할 일 :", tasks)

## 응용 실습
secret_number = 7
max_attempts = 3
attempt = 0
found = False

while attempt < max_attempts:
    guess = int(input("1~10 사이 숫자를 맞혀 보세요: "))
    attempt += 1

    # TODO: 정답이면 found를 True로 바꾸고 이번 추측을 출력한 뒤 break로 끝낸다.
    # TODO: 오답이면 이번 추측과 남은 기회를 출력한다.
    if guess == secret_number:
        found = True
        print(f"{attempt}번째 시도: {guess}를 선택하셨습니다. 정답")
        break
    ## elif를 사용할 필요가 없다.
    elif guess != secret_number:
        print(f"{attempt}번째 시도: {guess}를 선택하셨습니다. 오답. 남은 기회는 {max_attempts - attempt}번입니다.")

if found:
    print("최종 결과: 성공")
else:
    print("최종 결과: 실패")

