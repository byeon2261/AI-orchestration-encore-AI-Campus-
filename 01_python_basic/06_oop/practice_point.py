class Point:
    def __init__(self, x: int = 0, y: int = 0) -> None:
        # TODO: x와 y를 현재 객체의 속성으로 저장한다.
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> None:
        # TODO: 현재 객체의 x에는 dx를, y에는 dy를 더한다.
        self.x = self.x + dx
        self.y = self.y + dy

    def position(self) -> tuple[int, int]:
        # TODO: 현재 객체의 (x, y)를 반환한다.
        return (self.x, self.y)

    def is_origin(self) -> bool:
        # TODO: 현재 객체의 x와 y가 모두 0인지 반환한다.
        return self.x == 0 and self.y == 0


def main() -> None:
    first = Point(2, 1)
    second = Point()

    print(second.is_origin())
    first.move(-1, 3)
    second.move(0, 2)
    print(first.position())
    print(second.position())
    print(first.is_origin())


if __name__ == "__main__":
    main()