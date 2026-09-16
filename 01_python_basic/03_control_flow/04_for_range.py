repeat_count = int(input("스트레칭을 몇 번 할까요? "))

for count in range(1, repeat_count + 1):
    print(f"{count}) 스트레칭 완료")


## 응용 실습

dan = int(input("몇 단을 출력할까요? "))

# TODO: range()로 1부터 9까지 반복한다.
# TODO: 각 단계에서 "3 x 1 = 3" 형식으로 곱셈 결과를 출력한다.
for count in range(1, 10):
    print(f"{dan} x {count} = {dan * count}")