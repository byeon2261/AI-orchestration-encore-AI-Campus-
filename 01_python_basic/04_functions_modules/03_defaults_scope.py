def make_order_line(item: str, quantity: int = 1) -> str:
    line = f"{item} {quantity}개"
    return line


print("1) 기본 수량:", make_order_line("연필"))
print("2) 수량 지정:", make_order_line("공책", quantity=3))

# print(line)  # line은 함수 안에서 만든 지역 변수이므로 밖에서는 사용할 수 없다.