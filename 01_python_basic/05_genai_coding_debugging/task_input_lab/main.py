from validation import find_invalid_tasks


tasks = [
    {"작업 이름": "오류 로그 확인", "상태": "완료"},
    {"작업 이름": "API 응답 확인", "상태": "진행 중"},
    {"작업 이름": "", "상태": "대기"},
    {"작업 이름": "배포 대기", "상태": "멈춤"},
]

invalid_tasks = find_invalid_tasks(tasks)

for description in invalid_tasks:
    print(description)
