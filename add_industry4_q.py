import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

new_id = len(qs) + 1

new_q = {
    "question": "Những yếu tố cốt lõi của kỹ thuật số trong cách mạng công nghiệp lần thứ 4 là: (chọn 3 phương án)",
    "options": {
        "A": "Công nghệ 3D",
        "B": "Dữ liệu lớn (Big data)",
        "C": "Công nghệ sinh học",
        "D": "Vạn vật kết nối (IoT)",
        "E": "Trí tuệ nhân tạo (AI)"
    },
    "answer": "BDE",
    "explanation": "",
    "id": new_id,
    "type": "multi"
}

qs.append(new_q)
print(f"Added Q{new_id}. Total: {len(qs)}")

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("Synced to questions_clean.js")
