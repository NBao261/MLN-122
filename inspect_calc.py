import json
import re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print(f"Total questions: {len(qs)}")
calc_qs = [q for q in qs if q.get('type') == 'calc']
print(f"Current 'calc' count: {len(calc_qs)}")

for i, q in enumerate(calc_qs[:15]):
    print(f"[{i+1}] Q{q['id']}: {q['question'][:120]}")
