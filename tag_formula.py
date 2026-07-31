import json, re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Formula questions: those with actual math formulas/symbols in question or options
# NOT questions that merely discuss concepts like "tư bản bất biến"
formula_ids = set()

for q in qs:
    text = q['question'] + ' ' + ' '.join(q.get('options', {}).values())
    
    # Must have actual formula notation like X = Y, X' = Y, or choices with formula symbols
    has_formula_notation = bool(re.search(
        r"[WGKMTp]['\s]*=\s*[cvmptkWGKM\d(]|"        # W = c, K = c+v, m' = m/v, p' = m/(c+v)
        r"c\s*\+\s*v\s*\+\s*m|"                         # c + v + m
        r"c\s*\+\s*v\b|"                                  # c + v (as formula)
        r"v\s*\+\s*m\b|"                                  # v + m  
        r"m\s*\+\s*v\b|"                                  # m + v
        r"c\s*\+\s*m\b|"                                  # c + m
        r"m'\s*[=x×]|"                                   # m' = or m' x
        r"p'\s*=|"                                        # p' =
        r"T'\s*=|T'\s*[><]|"                             # T' = or T' > T
        r"n\s*=\s*CH|N\s*=\s*ch|"                        # n = CH/ch
        r"m/(c\+v)|m/\(c\+v\)|"                          # m/(c+v) ratio
        r"công thức.*tính.*bằng|tính bằng công thức|"     # explicit formula ask
        r"công thức cấu thành|"                           # formula composition
        r"ký hiệu là.*tính bằng",                         # symbol + formula ask
        text, re.IGNORECASE
    ))
    
    if has_formula_notation:
        formula_ids.add(q['id'])

# Exclude Q65 (multi-choice about chi phí sản xuất, no real formula)
# Exclude Q89, Q205, Q250, Q255, Q258, Q291, Q301, Q429, Q476 (theory about c/v, no formula notation)
# Keep only those with actual formula choices or formula in the stem
theory_only = {65, 89, 205, 250, 255, 258, 291, 301, 429, 476}
formula_ids -= theory_only

print(f"Formula question IDs ({len(formula_ids)}):")
for qid in sorted(formula_ids):
    q = next(x for x in qs if x['id'] == qid)
    print(f"  Q{qid}: {q['question'][:120]}")

# Now update types
for q in qs:
    if q['id'] in formula_ids:
        q['type'] = 'formula'

# Count types
type_counts = {}
for q in qs:
    t = q.get('type', 'single')
    type_counts[t] = type_counts.get(t, 0) + 1

print(f"\nFinal type breakdown:")
for t, c in sorted(type_counts.items()):
    print(f"  {t}: {c}")

# Save
with open('questions_clean.json', 'w', encoding='utf-8') as f:
    json.dump(qs, f, ensure_ascii=False, indent=2)

js = 'const QUESTIONS = ' + json.dumps(qs, ensure_ascii=False, indent=2) + ';'
with open('questions_clean.js', 'w', encoding='utf-8') as f:
    f.write(js)

print(f"\n✅ Saved {len(qs)} questions with formula type!")
