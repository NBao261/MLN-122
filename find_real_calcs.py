import json
import re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f"Total questions: {len(qs)}")

# Let's inspect questions that might be actual calculations:
potential_calcs = []
for q in qs:
    text = q['question'] + ' ' + ' '.join(q.get('options', {}).values())
    
    # Check for math/word problem indicators:
    # 1. USD, USD/tháng, $, %, công ty đầu tư, nhà tư bản đầu tư, công nhân, giá trị mới, m', p', W =, K =
    # 2. Words like "Tính", "tính bằng", "bằng bao nhiêu" combined with numbers or calculation context
    has_usd = bool(re.search(r'USD|\$|cho công nhân|hàng hóa tiêu dùng và|đầu tư \d|hao mòn máy móc|tính giá trị|tạo ra giá trị mới|trình độ bóc lột|m\' =|p\' =|W = c|K = c|G = c', text, re.IGNORECASE))
    has_math_problem = bool(re.search(r'\b(USD|\$|\d+\s*(USD|đôi|máy|giờ|công nhân|mét|lần))\b', text, re.IGNORECASE)) and ('tính' in text.lower() or 'bằng bao nhiêu' in text.lower() or 'đầu tư' in text.lower() or 'tạo ra' in text.lower() or 'bóc lột' in text.lower())

    if has_usd or has_math_problem:
        potential_calcs.append(q)

print(f"\nFound {len(potential_calcs)} potential calculation questions:")
for q in potential_calcs:
    print(f"\nQ{q['id']}: {q['question']}")
    print(f"   Options: {q['options']}")
    print(f"   Current type: {q.get('type')}")
