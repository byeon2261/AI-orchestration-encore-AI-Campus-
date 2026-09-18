from dataclasses import dataclass


@dataclass
class Product:
    name: str
    quantity: int


products = [
    Product("우유", 10),
    Product("빵", 5),
    Product("계란", 8),
]


def main() -> None:
    try:
        name = input("제품 이름을 입력하세요: ").strip()
        quantity = int(input("제품 수량을 입력하세요: "))

        if quantity < 0:
            raise ValueError("수량은 0 이상이어야 합니다.")

        if name == "":
            raise ValueError("제품 이름은 비어 있을 수 없습니다.")

        products.append(Product(name, quantity))
        print(f"제품 추가 완료되었습니다.")

    except ValueError as e:
        print(f"입력 오류: {e}")


def show_inventory() -> None:
    for number, product in enumerate(products, start=1):
        print(f"{number}. {product.name}: {product.quantity}")

    print(f"총 제품 수: {len(products)}")


if __name__ == "__main__":
    while True:
        choice = input(
            "어떤 작업을 하시겠습니까? "
            "(1. 재고 확인 2. 재고 추가) 번호를 입력해주세요. 종료(ctrl + c):"
        )

        if choice == "1":
            show_inventory()

        elif choice == "2":
            main()

        else:
            print("1 또는 2를 입력해주세요.")