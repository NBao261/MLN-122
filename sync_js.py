import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"Synced {len(qs)} questions to questions_clean.js")
