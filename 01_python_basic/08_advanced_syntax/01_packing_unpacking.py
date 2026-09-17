pair = "파이썬 입문", True
print("패킹:", pair)

title, finished = pair
print("언패킹:", title, finished)

book_fields = {"title": "파이썬 입문", "finished": True}
book = {"id": 1, **book_fields}
print("딕셔너리 언패킹:", book)
book = {"id": 1, "field": book_fields}
print("딕셔너리 삽입:", book)