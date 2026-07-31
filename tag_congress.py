import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# IDs of Đại hội Đảng questions
congress_ids = {36, 39, 88, 98, 113, 118, 134, 174, 194, 311, 413, 414}

count = 0
for q in qs:
    if q['id'] in congress_ids:
        q['type'] = 'congress'
        count += 1

print(f"Tagged {count} questions as 'congress'")

# Count types
type_counts = {}
for q in qs:
    t = q.get('type', 'single')
    type_counts[t] = type_counts.get(t, 0) + 1

print("\nFinal type breakdown:")
for t, c in sorted(type_counts.items()):
    print(f"  {t}: {c}")

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"\n✅ Saved {len(qs)} questions!")
