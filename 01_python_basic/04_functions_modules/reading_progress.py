# TODO: 목표 시간과 읽은 시간을 받는 함수를 def로 직접 정의한다.
# TODO: 목표까지 남은 시간을 계산해 return한다. 목표를 달성했으면 0을 반환한다. 
def calculate_reading_progress(target_time: int, read_time: int) -> int:
    if read_time >= target_time:
        return 0
    time_left = target_time - read_time
    return time_left