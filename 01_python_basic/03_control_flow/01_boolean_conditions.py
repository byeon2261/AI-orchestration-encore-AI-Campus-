is_member = input("회원인가요? (y/n): ") == "y"
order_amount = int(input("주문 금액을 입력하세요: "))

can_get_free_shipping = is_member and order_amount >= 30000
can_use_coupon = is_member or order_amount >= 50000
needs_shipping_fee = not can_get_free_shipping

print("1) 무료 배송 가능 여부:", can_get_free_shipping)
print("2) 쿠폰 사용 가능 여부:", can_use_coupon)
print("3) 배송비 필요 여부:", needs_shipping_fee)