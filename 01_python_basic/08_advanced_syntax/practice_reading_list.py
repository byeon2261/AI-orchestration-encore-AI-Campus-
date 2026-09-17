"""독서 목록을 컴프리헨션과 번호 붙이기로 정리한다."""


from turtle import title


def pending_titles(titles: list[str], finished: list[bool]) -> list[str]:
    # TODO: zip()으로 같은 위치의 제목과 완료 여부를 짝짓는다.
    # TODO: 리스트 컴프리헨션으로 완료하지 않은 제목만 새 목록에 담는다.
    return [title 
            for title, finished in zip(titles, finished) 
            if not finished]


def numbered_titles(titles: list[str]) -> list[str]:
    # TODO: enumerate(titles, start=1)로 번호와 제목을 함께 꺼낸다.
    # TODO: "1. 파이썬 입문" 형태의 문자열 목록을 반환한다.
    return [f"{number}. {title}" 
            for number, title in enumerate(titles, start=1)]


def main() -> None:
    titles = ["파이썬 입문", "자료구조", "알고리즘"]
    finished = [True, False, False]

    print("읽을 책:", pending_titles(titles, finished))
    print("번호 목록:", numbered_titles(titles))


if __name__ == "__main__":
    main()