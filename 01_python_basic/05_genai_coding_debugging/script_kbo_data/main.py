"""구단명을 입력해 오늘 상대 팀과 KBO 공식 기록을 비교합니다.

Python 3.10 이상 / 설치: python -m pip install beautifulsoup4
실행: python kbo_today.py
"""

import re
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup

RANK_URL = "https://www.koreabaseball.com/Record/TeamRank/TeamRankDaily.aspx"
SCOREBOARD_URL = "https://www.koreabaseball.com/Schedule/ScoreBoard.aspx"
KST = timezone(timedelta(hours=9))
TEAMS = {
    "KIA": ["기아", "기아타이거즈", "kia타이거즈", "타이거즈"],
    "삼성": ["삼성라이온즈", "라이온즈"],
    "LG": ["엘지", "엘지트윈스", "lg트윈스", "트윈스"],
    "두산": ["두산베어스", "베어스"],
    "KT": ["케이티", "kt위즈", "케이티위즈", "위즈"],
    "SSG": ["에스에스지", "ssg랜더스", "에스에스지랜더스", "랜더스"],
    "롯데": ["롯데자이언츠", "자이언츠"],
    "한화": ["한화이글스", "이글스"],
    "NC": ["엔씨", "nc다이노스", "엔씨다이노스", "다이노스"],
    "키움": ["키움히어로즈", "히어로즈"],
}


def normalize_team(value):
    """공백과 영문 대소문자를 무시하고 정식 약칭을 반환합니다."""
    value = re.sub(r"\s+", "", value).casefold()
    for team, aliases in TEAMS.items():
        if value in [name.casefold() for name in [team, *aliases]]:
            return team
    raise ValueError("구단명을 확인해 주세요: " + ", ".join(TEAMS))


def text_at(element, selector, default="미제공"):
    node = element.select_one(selector)
    return node.get_text(" ", strip=True) or default if node else default


def parse_records(html):
    """표의 열 제목을 기준으로 공식 기록을 읽습니다."""
    soup = BeautifulSoup(html, "html.parser")
    date = text_at(soup, "span[id$='lblSearchDateTitle']", "")
    if not re.fullmatch(r"\d{4}\.\d{2}\.\d{2}", date):
        raise ValueError("기록 기준일을 확인할 수 없습니다.")

    standings = {}
    matchups = {}
    for table in soup.select("table"):
        headers = [node.get_text(" ", strip=True) for node in table.select("thead th")]
        is_standings = all(key in headers for key in ["팀명", "승률", "최근10경기"])
        is_matchups = any("(승-패-무)" in key for key in headers)
        if not (is_standings or is_matchups):
            continue
        for row in table.select("tbody tr"):
            values = [node.get_text(" ", strip=True) for node in row.select("th, td")]
            if len(values) != len(headers):
                raise ValueError("KBO 기록 표의 형식이 변경되었습니다.")
            record = dict(zip(headers, values))
            team = normalize_team(record["팀명"])
            if is_standings:
                standings[team] = record
            else:
                matchups[team] = {
                    key.split()[0]: value
                    for key, value in record.items() if "(승-패-무)" in key
                }
    if not standings or not matchups:
        raise ValueError("팀 순위 또는 상대 전적을 확인할 수 없습니다.")
    return date, standings, matchups


def win_rate(wins, losses):
    """무승부는 승률 계산에서 제외하고, 승패가 없으면 None을 반환합니다."""
    return wins / (wins + losses) if wins + losses else None


def recent_rate(record):
    match = re.fullmatch(r"(\d+)승\s*(\d+)무\s*(\d+)패", record)
    if not match:
        return None
    wins, draws, losses = map(int, match.groups())
    return win_rate(wins, losses)


def season_rate(record):
    if not record["승"].isdigit() or not record["패"].isdigit():
        return None
    return win_rate(int(record["승"]), int(record["패"]))


def compare(label, first, second, first_value, second_value):
    if first_value is None or second_value is None:
        return f"{label}: 비교할 기록 부족"
    if abs(first_value - second_value) < 0.000001:
        return f"{label}: 동일"
    leader = first if first_value > second_value else second
    return f"{label}: {leader} 우세 (승률 차이 {abs(first_value - second_value):.1%}p)"


def fetch_html(url):
    request = Request(url, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
    with urlopen(request, timeout=20) as response:
        return response.read().decode("utf-8-sig")


def find_today_opponent(team):
    """오늘 스코어보드에서 입력 팀의 상대 팀과 경기 정보를 찾습니다."""
    soup = BeautifulSoup(fetch_html(SCOREBOARD_URL), "html.parser")
    game_date = text_at(soup, "span[id$='lblGameDate']", "")
    if not game_date.startswith(datetime.now(KST).strftime("%Y.%m.%d")):
        raise ValueError("오늘 스코어보드를 확인할 수 없습니다.")
    matches = []
    for card in soup.select(".smsScore"):
        away = text_at(card, ".leftTeam .teamT", "")
        home = text_at(card, ".rightTeam .teamT", "")
        if away and home and team in [normalize_team(away), normalize_team(home)]:
            opponent = normalize_team(home if normalize_team(away) == team else away)
            place = card.select_one(".place")
            stadium = " ".join(place.stripped_strings) if place else "미제공"
            matches.append((opponent, stadium, text_at(card, ".flag", "경기 예정")))
    if not matches:
        raise ValueError(f"오늘({datetime.now(KST):%Y-%m-%d}) {team} 경기가 없습니다.")
    if len(matches) > 1:
        raise ValueError(f"오늘 {team} 경기가 여러 개입니다. 스코어보드에서 더블헤더를 확인해 주세요.")
    return matches[0]


def analyze_today_game(team_name):
    first = normalize_team(team_name)
    second, stadium, status = find_today_opponent(first)
    html = fetch_html(RANK_URL)
    date, standings, matchups = parse_records(html)
    if first not in standings or second not in standings:
        raise ValueError("선택한 팀의 시즌 기록이 없습니다.")

    lines = [f"\n오늘 경기: {first} vs {second}", f"경기 정보: {stadium} | {status}", f"기록 기준일: {date}"]
    for team in [first, second]:
        record = standings[team]
        lines.append(
            f"{team}: {record['순위']}위 | {record['경기']}경기 | "
            f"{record['승']}승 {record['무']}무 {record['패']}패 | 승률 {record['승률']}\n"
            f"  최근 10경기: {record['최근10경기']} | 연속: {record['연속']}"
        )
    lines.append(compare("시즌 성적", first, second,
                         season_rate(standings[first]), season_rate(standings[second])))
    lines.append(compare("최근 흐름", first, second,
                         recent_rate(standings[first]["최근10경기"]),
                         recent_rate(standings[second]["최근10경기"])))
    head_to_head = matchups.get(first, {}).get(second, "")
    match = re.fullmatch(r"(\d+)-(\d+)-(\d+)", head_to_head)
    if match:
        wins, losses, draws = map(int, match.groups())
        lines.append(f"상대 전적 ({first} 기준): {wins}승 {losses}패 {draws}무")
        lines.append(compare("맞대결 성적", first, second,
                             win_rate(wins, losses), win_rate(losses, wins)))
    else:
        lines.append("상대 전적: 비교할 기록 부족")
    lines.append("분석 범위: 시즌 성적·최근 흐름·맞대결 기록. 선발투수·부상·라인업은 미반영.")
    lines.append("각 지표의 우세는 기록 비교이며, 다음 경기의 승리 확률은 아닙니다.")
    return "\n".join(lines)


def main():
    print("조회 가능한 구단: " + ", ".join(TEAMS))
    try:
        team = input("구단명: ")
        print(analyze_today_game(team))
        print(f"\n조회 시각: {datetime.now(KST):%Y-%m-%d %H:%M:%S} KST")
        print(f"출처: {SCOREBOARD_URL}")
        print(f"기록 출처: {RANK_URL}")
    except HTTPError as error:
        print(f"KBO 서버 요청 실패: HTTP {error.code}")
    except (URLError, TimeoutError, OSError) as error:
        print(f"네트워크 오류: {error}")
    except (ValueError, KeyError) as error:
        print(f"분석 실패: {error}")
    except (EOFError, KeyboardInterrupt):
        print("\n분석을 종료합니다.")


if __name__ == "__main__":
    main()
