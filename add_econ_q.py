import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

new_id = len(qs) + 1

new_q = {
    "question": "Trong nền kinh tế thị trường định hướng xã hội chủ nghĩa, thành phần kinh tế nào giữ vai trò chủ đạo?",
    "options": {
        "A": "Thành phần kinh tế nhà nước",
        "B": "Thành phần kinh tế tư nhân",
        "C": "Thành phần kinh tế tập thể",
        "D": "Thành phần kinh tế có vốn đầu tư nước ngoài"
    },
    "answer": "A",
    "explanation": "Đề chưa rõ, nếu \"chủ đạo\" thì là nhà nước, còn \"động lực\" thì là tư nhân",
    "id": new_id,
    "type": "single"
}

qs.append(new_q)
print(f"Added Q{new_id}. Total: {len(qs)}")

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Synced to questions_clean.js")
