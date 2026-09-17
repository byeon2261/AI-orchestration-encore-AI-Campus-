def parse_quantity(raw_value: str) -> int:
    quantity = int(raw_value)

    if quantity < 0:
        raise ValueError("수량은 0 이상이어야 한다.")

    return quantity


for sample in ["3", "unknown", "-2", "0"]:
    try:
        print(f"{sample!r} -> {parse_quantity(sample)}개")
    except ValueError as error:
        print(f"{sample!r} 처리 실패: {error}")