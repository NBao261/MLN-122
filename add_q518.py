import json

q = {
    "id": 518,
    "question": "Điều kiện để ra đời và tồn tại của sản xuất hàng hóa:",
    "options": {
        "A": "Số lượng hàng hoá làm ra trong một đơn vị thời gian tăng lên",
        "B": "Số lượng lao động hao phí trong thời gian đó không thay đổi",
        "C": "Giá trị 1 đơn vị hàng hoá giảm đi"
    },
    "answer": ["A"],
    "type": "1_option"
}

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
    
data.append(q)

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write("const QUESTIONS = " + json.dumps(data, ensure_ascii=False, indent=2) + ";")
