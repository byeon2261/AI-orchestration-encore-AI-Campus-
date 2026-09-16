from reading_progress import calculate_reading_progress


goal_minutes = int(input("목표 독서 시간(분): "))
read_minutes = int(input("오늘 읽은 시간(분): "))

remaining_minutes = -1

# TODO: reading_progress에 직접 만든 함수를 호출해 반환값을 remaining_minutes에 저장한다.
remaining_minutes = calculate_reading_progress(goal_minutes, read_minutes)

print("1) 목표 시간(분):", goal_minutes)
print("2) 읽은 시간(분):", read_minutes)
print("3) 남은 시간(분):", remaining_minutes)