import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print("=== CHECKING ALL QUESTIONS FOR NUMERICAL CALCULATIONS ===")
for q in qs:
    text = q['question']
    # Look for USD, $, numbers like 100, 5000, 1000, 500.000, etc.
    if any(k in text for k in ['USD', '$', '100 công nhân', '50 USD', '100000', '5000', 'bóc lột']) or ('tính' in text.lower() and any(c.isdigit() for c in text)):
        print(f"Q{q['id']}: {text[:150]}")
