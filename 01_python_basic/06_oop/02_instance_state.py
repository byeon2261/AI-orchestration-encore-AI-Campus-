class Counter:
    created_count = 0

    def __init__(self, start: int = 0) -> None:
        self.value = start
        Counter.created_count += 1

    def increment(self) -> None:
        self.value += 1


first = Counter()
second = Counter(start=10)

first.increment()
first.increment()
second.increment()

print(first.value)
print(second.value)
print(Counter.created_count)

a = Counter()
print(a.value)
print(first.value)
print(Counter.created_count)