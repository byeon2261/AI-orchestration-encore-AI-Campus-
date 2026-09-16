def calculate_delivery_fee(order_total: int) -> int:
    if order_total >= 30000:
        return 0
    return 3000

## import 되는 경우에는 실행되지 않는다.
if __name__ == "__main__":
    print("테스트) 배송비 단독 확인:", calculate_delivery_fee(12000))