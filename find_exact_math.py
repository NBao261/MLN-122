import json
import re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print("=== SEARCHING ALL QUESTIONS WITH NUMBERS & MATH FORMULAS ===")

math_candidates = []
for q in qs:
    qtext = q['question']
    opts = ' '.join(q.get('options', {}).values())
    full_text = qtext + ' ' + opts
    
    # Look for math problem indicators:
    # 1. Contains numbers in calculation context (USD, %, W =, K =, p' =, m' =, c =, v =, m =, công nhân, đầu tư...)
    # 2. Formula choices like K = c + v, p' = ..., m' = ...
    # 3. Calculation word problems
    
    # Check if numbers are used in mathematical/numerical context (not just year or option count)
    is_calc_problem = False
    
    # Specific math word problems
    if re.search(r'\b\d+[\d\.,]*\s*(USD|\$|đối dép|mét vải|người|giờ|công nhân)\b', full_text, re.IGNORECASE):
        is_calc_problem = True
    elif re.search(r'USD|tính giá trị|tạo ra giá trị mới|trình độ bóc lột|m\' =|p\' =|W =|K =|G =|M =', full_text, re.IGNORECASE):
        # But exclude non-calc general questions like "Công thức tính..." if it's purely theoretical choice, OR keep formula questions as calc?
        # User said: "Cũng như những câu này không phải là câu tính toán, câu tính toán là những câu như: Cứ 100 công nhân... Để sản xuất ra 1000 đối dép..."
        # So user wants ONLY actual numerical math problems / exercises as "Câu tính toán"!
        if re.search(r'\d+[\d\.,]*', full_text) and not re.search(r'khoảng bao nhiêu năm|mấy giai đoạn|mấy thuộc tính|bao nhiêu thuộc tính|bao nhiêu mặt|năm \d{4}|thế kỷ|lần thứ \d', qtext, re.IGNORECASE):
            is_calc_problem = True

    if is_calc_problem:
        math_candidates.append(q)

print(f"Total candidate questions: {len(math_candidates)}")
for q in math_candidates:
    print(f"\nQ{q['id']}: {q['question']}")
    print(f"   Options: {q['options']}")
    print(f"   Answer: {q['answer']}")
