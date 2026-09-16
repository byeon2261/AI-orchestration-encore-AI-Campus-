def calculate_ticket_price(age: int, is_weekend: bool) -> int:
    if age < 19:
        return 7000
    if is_weekend:
        return 15000
    return 12000