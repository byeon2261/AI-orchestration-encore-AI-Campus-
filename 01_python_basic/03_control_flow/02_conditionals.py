score = int(input("점수를 입력하세요: "))

if score >= 90:
    grade = "A"
elif score >= 80:
    grade = "B"
elif score >= 70:
    grade = "C"
else:
    grade = "재도전"

print("1) 입력한 점수:", score)
print("2) 성적:", grade)

## 응용 예시

age = int(input("나이를 입력하세요: "))
is_weekend = input("주말인가요? (y/n): ") == "y"

ticket_price = -1
# TODO: if, elif, else로 나이와 주말 여부에 따른 가격을 결정한다.

print("1) 관람객 나이:", age)
print("2) 주말 여부:", is_weekend)
print("3) 영화표 가격:", ticket_price)