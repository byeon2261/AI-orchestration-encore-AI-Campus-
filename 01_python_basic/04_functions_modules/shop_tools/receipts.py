def format_receipt(item: str, order_total: int, delivery_fee: int) -> str:
    final_total = order_total + delivery_fee
    return f"{item}: 상품 {order_total}원 + 배송 {delivery_fee}원 = {final_total}원"