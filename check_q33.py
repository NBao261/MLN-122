import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Find question around index 33 (0-indexed = 32)
for i in range(30, 36):
    q = qs[i]
    print(f"--- Q{q['id']} (index {i}) ---")
    print(f"Question: {q['question'][:300]}")
    print(f"Options: {q.get('options', {})}")
    print(f"Answer: {q['answer']}")
    print()

# Also search for 'Tich tu' keyword
print("\n=== Search for 'Tích tụ và tập trung' ===")
for i, q in enumerate(qs):
    if 'Tích tụ và tập trung' in q['question'] or 'Tiền công thực tế là' in q['question']:
        print(f"Index {i}, Q{q['id']}: {q['question'][:300]}")
        print(f"  Answer: {q['answer']}")
        print()
