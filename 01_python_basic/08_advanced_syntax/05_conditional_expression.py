is_finished = False

if is_finished:
    label_with_if = "완료"
else:
    label_with_if = "읽는 중"

label = "완료" if is_finished else "읽는 중"
print(label_with_if, label)