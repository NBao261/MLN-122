"""
Add the 6 unique 'Kiểu hỏi khác' questions that have options to the main dataset.
For answers, we'll infer based on the context in the PDF (the 'Kiểu hỏi khác' 
appears right after the original question with known answer, and these are 
rephrased versions with different options).
"""
import json, re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f"Current: {len(qs)} questions")

# The 6 unique Kiểu hỏi khác with their options and correct answers
# (answers determined from the PDF context and subject knowledge)
new_questions = [
    {
        "question": "Khi nghiên cứu về cách mạng công nghiệp lần thứ nhất, C. Mác đã khái quát tính quy luật của các mạng công nghiệp qua các giai đoạn phát triển đó là:",
        "options": {
            "A": "Hiệp tác đơn giản, lao động thủ công, lao động phức tạp",
            "B": "Hiệp tác đơn giản, công trường thủ công, công nghiệp hóa",
            "C": "Hiệp tác đơn giản, sản xuất thủ công, sản xuất hiện đại",
            "D": "Hiệp tác đơn giản, công trường thủ công, đại công nghiệp"
        },
        "answer": "D",
        "explanation": "",
        "type": "single"
    },
    {
        "question": "Nguồn gốc nào không đúng với nguồn vốn công nghiệp hóa ở các nước tư bản cổ điển?",
        "options": {
            "A": "Cướp bóc thuộc địa",
            "B": "Khai thác lao động làm thuê",
            "C": "Làm phá sản những người sản xuất nhỏ trong nông nghiệp",
            "D": "Đi vay nhà nước"
        },
        "answer": "D",
        "explanation": "",
        "type": "single"
    },
    {
        "question": "Xuất khẩu hàng hóa là một trong những đặc điểm của:",
        "options": {
            "A": "Sản xuất hàng hóa giản đơn",
            "B": "Phương thức sản xuất tư bản chủ nghĩa",
            "C": "Giai đoạn chủ nghĩa tư bản tự do cạnh tranh",
            "D": "Giai đoạn chủ nghĩa tư bản độc quyền"
        },
        "answer": "D",
        "explanation": "",
        "type": "single"
    },
    {
        "question": "Tích lũy tư bản là gì?",
        "options": {
            "A": "Tư bản hóa tư liệu tiêu dùng",
            "B": "Tư bản hóa giá trị thặng dư",
            "C": "Tư bản hóa sức lao động",
            "D": "Tư bản hóa giá trị sản xuất"
        },
        "answer": "B",
        "explanation": "",
        "type": "single"
    },
    {
        "question": "Ai là người đầu tiên đưa ra khái niệm \"kinh tế chính trị\"?",
        "options": {
            "A": "Francois Quesney",
            "B": "Antoine Montchretiên",
            "C": "William Petty"
        },
        "answer": "B",
        "explanation": "",
        "type": "single"
    },
    {
        "question": "Về kinh tế, xuất khẩu tư bản nhà nước thường hướng vào:",
        "options": {
            "A": "Ngành kết cấu hạ tầng",
            "B": "Ngành có vốn chu chuyển nhanh",
            "C": "Ngành công nghệ mới"
        },
        "answer": "A",
        "explanation": "",
        "type": "single"
    },
]

# Append to existing questions
for nq in new_questions:
    nq['id'] = len(qs) + 1
    qs.append(nq)

print(f"After adding 6 Kiểu hỏi khác: {len(qs)} questions")

# Also check the 4 dedup'd questions that were removed
# Re-check if dedup removed any that were actually different
seen = {}
dupes = []
for q in qs:
    key = re.sub(r'\s+', '', q['question']).lower()
    if key in seen:
        dupes.append((q['id'], seen[key], q['question'][:80]))
    else:
        seen[key] = q['id']

if dupes:
    print(f"\nDuplicate pairs found: {len(dupes)}")
    for qid, orig_id, text in dupes:
        print(f"  Q{qid} = Q{orig_id}: {text}")
else:
    print("No duplicates")

# Save
with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"\n✅ Saved {len(qs)} questions to questions_clean.json and questions_clean.js")
