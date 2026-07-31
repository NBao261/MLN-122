import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

for q in qs:
    if q['id'] == 83:
        q['explanation'] = "W = c + v + m\nc = 100000 + 5000 = 105000\nv = 5000\nm = m' × v = 2 × 5000 = 10000\nW = 105000 + 5000 + 10000 = 120000 USD"
        print(f"Updated Q83 explanation: {q['explanation']}")
        break

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("✅ Saved!")
