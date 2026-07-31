import json
import re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

print("=== ALL CURRENT 61 CALC QUESTIONS ===")
for q in qs:
    if q.get('type') == 'calc':
        print(f"Q{q['id']}: {q['question']}")
        print(f"   Options: {q['options']}")
        print()
