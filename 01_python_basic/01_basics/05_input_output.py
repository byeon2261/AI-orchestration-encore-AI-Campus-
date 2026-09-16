name = input("이름: ").strip()
study_minutes_text = input("학습 시간(분): ").strip()

study_minutes = int(study_minutes_text)
study_hours = study_minutes / 60

print(f"{name}의 학습 시간은 {study_hours:.1f}시간이다.")