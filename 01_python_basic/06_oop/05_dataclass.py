from dataclasses import dataclass


@dataclass
class BookRecord:
    title: str
    author: str


first_record = BookRecord("파이썬 첫걸음", "김하늘")
same_record = BookRecord("파이썬 첫걸음", "김하늘")

print(first_record)
## 데이터 클래스를 상속받지 않고 비교하면 False가 나온다.
print(first_record == same_record)