def parse_quantity(raw_value: str) -> int:
    return int(raw_value)


def describe_order(raw_quantity: str) -> str:
    quantity = parse_quantity(raw_quantity)
    return f"노트 {quantity}권"


def main() -> None:
    print(describe_order("2"))
    print(describe_order("unknown"))


if __name__ == "__main__":
    main()