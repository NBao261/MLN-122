import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Ensure calc questions stay as calc (not formula)
calc_ids = {80, 83, 467}
for q in qs:
    if q['id'] in calc_ids:
        q['type'] = 'calc'

# Count
type_counts = {}
for q in qs:
    t = q.get('type', 'single')
    type_counts[t] = type_counts.get(t, 0) + 1

print("Final type breakdown:")
for t, c in sorted(type_counts.items()):
    print(f"  {t}: {c}")

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("✅ Fixed!")
