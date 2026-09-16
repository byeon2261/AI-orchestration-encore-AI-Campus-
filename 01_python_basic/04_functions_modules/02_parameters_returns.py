def calculate_ticket_price(age: int, is_weekend: bool) -> int:
    if age < 19:
        return 7000
    if is_weekend:
        return 15000
    return 12000


teen_price = calculate_ticket_price(18, True)
adult_weekend_price = calculate_ticket_price(19, True)

print("1) 청소년 주말 가격:", teen_price)
print("2) 성인 주말 가격:", adult_weekend_price)
print("3) 성인 2명 주말 합계:", adult_weekend_price * 2)