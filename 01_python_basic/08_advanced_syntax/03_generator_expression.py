"""제너레이터 표현식을 합계와 조건 확인에 사용한다."""

numbers = [1, 4, 2, 3]

square_values = (number * number for number in numbers)
print("제곱 합계:", sum(square_values))

has_large_square = any(number * number > 10 for number in numbers)
print("10보다 큰 제곱이 있는가:", has_large_square)