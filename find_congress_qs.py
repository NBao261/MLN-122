import json, re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Search for questions related to "Đại hội Đảng"
keywords = [
    'đại hội', 'Đại hội', 'ĐẠI HỘI',
    'Đảng Cộng sản', 'Đảng cộng sản',
    'Văn kiện', 'văn kiện',
    'nghị quyết', 'Nghị quyết',
    'Đại hội đại biểu',
    'Đại hội XI', 'Đại hội X', 'Đại hội IX', 'Đại hội VIII', 'Đại hội VII',
    'Đại hội VI', 'Đại hội V', 'Đại hội IV', 'Đại hội III',
    'đại hội đảng', 'đại hội mấy',
]

congress_qs = []
for q in qs:
    text = q['question'] + ' ' + ' '.join(q.get('options', {}).values())
    if any(kw in text for kw in keywords):
        congress_qs.append(q)

print(f"Found {len(congress_qs)} questions related to Đại hội Đảng:\n")
for q in congress_qs:
    print(f"Q{q['id']} [{q.get('type')}]: {q['question'][:150]}")
    # Show if any option mentions đại hội
    for k, v in q.get('options', {}).items():
        if any(kw in v for kw in ['đại hội', 'Đại hội', 'Nghị quyết', 'Văn kiện']):
            print(f"     {k}: {v[:100]}")
    print()
