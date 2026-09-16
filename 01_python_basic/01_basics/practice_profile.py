name = input("이름: ").strip()
study_minutes_text = input("학습 시간(분): ").strip()
learning_goal = input("학습 목표: ").strip()

# TODO: study_minutes_text를 정수로 변환한다.
study_minutes = int(study_minutes_text)
# TODO: 학습 시간을 시간 단위로 계산한다.
stuedy_hours = study_minutes / 60
# TODO: 이름, 학습 시간, 학습 목표를 f-string 한 줄로 출력한다.
print(f"{name}의 학습 시간은 {stuedy_hours:.1f}시간이며 학습 목표는 {learning_goal}을 학습한다.")



name = input("이름: ").strip()
study_minutes_text = input("학습 시간(분): ").strip()
learning_goal = input("학습 목표: ").strip()

study_minutes = int(study_minutes_text)
stuedy_hours = study_minutes / 60
print(f"{name}의 학습 시간은 {stuedy_hours:.1f}시간이며 학습 목표는 {learning_goal}을 학습한다.")