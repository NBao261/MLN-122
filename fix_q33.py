import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Find Q33 (id=33 or index 32)
for i, q in enumerate(qs):
    if q['id'] == 33:
        print(f"Before fix:")
        print(f"  Question: {q['question']}")
        # Fix: strip the erroneously prepended preamble
        # The real question is just "Tiền công thực tế là"
        q['question'] = 'Tiền công thực tế là'
        print(f"After fix:")
        print(f"  Question: {q['question']}")
        print(f"  Answer: {q['answer']}")
        print(f"  Options: {q['options']}")
        break

with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

# Rebuild JS file
js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print("\n✅ Fixed and saved!")
