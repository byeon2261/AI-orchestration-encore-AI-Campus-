"""문자열로 받은 두 수를 나누고 예상 가능한 오류를 안내한다."""


def divide(raw_number: str, raw_divisor: str) -> float:
    number = int(raw_number)
    divisor = int(raw_divisor)
    return number / divisor


def describe_division(raw_number: str, raw_divisor: str) -> str:
    try:
        number = divide(raw_number, raw_divisor)
    except ValueError as error:
        return f"숫자를 입력해야 한다.: {error}"
    except ZeroDivisionError as error:
        return f"0으로 나눌 수 없다.: {error}"
    else:
        return f"계산 결과: {number}"

def main() -> None:
    cases = [
        ("12", "3"),
        ("12", "0"),
        ("열둘", "3"),
        ("7", "2"),
    ]

    for number, divisor in cases:
        print(f"{number} / {divisor}: {describe_division(number, divisor)}")


if __name__ == "__main__":
    main()