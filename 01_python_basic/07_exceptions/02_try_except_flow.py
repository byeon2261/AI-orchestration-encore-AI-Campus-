def parse_minutes(raw_value: str) -> int | None:
    try:
        minutes = int(raw_value)
    except ValueError as error:
        print(f"{raw_value!r} 변환 실패: {error}")
        return None
    else:
        print(f"{raw_value!r} 변환 성공")
        return minutes
    finally:
        print("입력 처리를 종료한다.")


for sample in ["45", "unknown", "0"]:
    result = parse_minutes(sample)
    print(f"결과: {result}\n")