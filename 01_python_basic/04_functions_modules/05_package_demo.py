from shop_tools.delivery import calculate_delivery_fee
from shop_tools.receipts import format_receipt


first_total = 12000
first_fee = calculate_delivery_fee(first_total)
print("1) 첫 주문:", format_receipt("연필 세트", first_total, first_fee))

second_total = 35000
second_fee = calculate_delivery_fee(second_total)
print("2) 두 번째 주문:", format_receipt("노트 묶음", second_total, second_fee))