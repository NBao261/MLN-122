import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f"Total questions before: {len(qs)}")

# 1. Fix Q84 stem (remove Q83 working solution from stem)
for q in qs:
    if q['id'] == 83:
        q['explanation'] = "W = c + v + m = 100000 + 5000 + (5000 x 200%) = 105000 + 10000 = 115000 USD (cho 1000 đôi dệt). Cho 10.000 đôi = 1.150.000 USD."
    if q['id'] == 84:
        if 'Nhận xét dưới đây' in q['question']:
            q['question'] = "Nhận xét dưới đây về phương pháp sản xuất giá trị thặng dư tuyệt đối, nhận xét nào là không đúng?"

# 2. Fix Q367
for q in qs:
    if q['id'] == 367:
        q['question'] = "Gọi W là giá trị hàng hóa, vậy công thức tính giá trị hàng hóa là gì?"
        q['options'] = {
            "A": "W = c + v + m",
            "B": "W = c + v",
            "C": "W = v + m",
            "D": "W = (c + v) / m"
        }
        q['answer'] = "A"

# Check if Page 127 crisis question already exists
has_crisis_q = any("Cuộc khủng hoảng nào đã làm phá sản" in q['question'] for q in qs)
if not has_crisis_q:
    new_q = {
        "id": len(qs) + 1,
        "question": "Cuộc khủng hoảng nào đã làm phá sản doanh nghiệp vừa và nhỏ, các doanh nghiệp lớn còn tồn tại dẫn tới hình thành các doanh nghiệp độc quyền đầu tiên?",
        "options": {
            "A": "Khủng hoảng kinh tế năm 1873",
            "B": "Khủng hoảng kinh tế năm 1928",
            "C": "Khủng hoảng kinh tế năm 1973",
            "D": "Khủng hoảng kinh tế năm 2021"
        },
        "answer": "A",
        "explanation": "",
        "type": "single"
    }
    qs.append(new_q)
    print(f"Added Page 127 crisis question as Q{new_q['id']}")

# 3. Define calculation question IDs (actual numerical exercises)
# Q80, Q83, Q467 are true calculation exercises
calc_ids = set()
for q in qs:
    text = q['question'] + ' ' + ' '.join(q.get('options', {}).values())
    # True numerical exercises: contains specific numbers (USD, $, đôi dép, mét vải, công nhân) asking for numerical calculation
    if any(phrase in q['question'] for phrase in [
        'Cứ 100 công nhân thì tạo ra giá trị mới',
        'Để sản xuất ra 1000 đối dép',
        'Cho ví dụ: nhà tư bản đầu tư 50 USD'
    ]):
        calc_ids.add(q['id'])

print(f"\nCalculation question IDs: {calc_ids}")

# 4. Update types for all questions
calc_count = 0
multi_count = 0
single_count = 0

for q in qs:
    ans = q.get('answer', '')
    if q['id'] in calc_ids:
        q['type'] = 'calc'
        calc_count += 1
    elif len(ans) > 1 and ans not in ['A', 'B', 'C', 'D']:
        q['type'] = 'multi'
        multi_count += 1
    else:
        # Check if question stem mentions (chọn nhiều đáp án)
        if '(chọn nhiều' in q['question'].lower() or 'chọn nhiều đáp án' in q['question'].lower():
            q['type'] = 'multi'
            multi_count += 1
        else:
            q['type'] = 'single'
            single_count += 1

print(f"\nRe-classified question types:")
print(f"  - Single choice: {single_count}")
print(f"  - Multi choice: {multi_count}")
print(f"  - Calculation (Tính toán bài tập): {calc_count}")
print(f"  - Total: {len(qs)}")

# Save JSON and JS
with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("\n✅ Successfully updated questions_clean.json and questions_clean.js!")
