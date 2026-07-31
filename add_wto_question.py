import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

new_id = len(qs) + 1

new_q = {
    "question": "Việt Nam trở thành thành viên chính thức của tổ chức thương mại kinh tế thế giới WTO khi nào?",
    "options": {
        "A": "2007",
        "B": "2006",
        "C": "2005",
        "D": "2008"
    },
    "answer": "A",
    "explanation": "Gia nhập năm 2006, trở thành thành viên năm 2007",
    "id": new_id,
    "type": "single"
}

qs.append(new_q)
print(f"Added new question as Q{new_id}. Total questions: {len(qs)}")

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"Synced {len(qs)} questions to questions_clean.js")
