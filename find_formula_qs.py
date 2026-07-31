import json, re

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

# Find questions that involve formulas (W=, K=, m'=, p'=, G=, T'=, M=, etc.)
formula_qs = []
for q in qs:
    text = q['question'] + ' ' + ' '.join(q.get('options', {}).values())
    # Look for formula patterns
    has_formula = bool(re.search(
        r"[WGKMTkmp]['\s]*=\s*[cvmptkWGKM]|"  # W = c, K = c, m' = , p' = , G = c, M = m'
        r"m'\s*=|p'\s*=|T'\s*=|W\s*=\s*[cvCVM]|K\s*=\s*[cvm]|G\s*=\s*[ckvCKV]|M\s*=\s*m|"
        r"công thức.*tính|tính bằng công thức|công thức.*giá trị|"
        r"ký hiệu là.*tính bằng|"
        r"tỷ suất.*công thức|công thức.*tỷ suất|"
        r"chi phí sản xuất.*tính bằng|"
        r"c \+ v \+ m|c\+v\+m|"
        r"tư bản bất biến.*tư bản khả biến|"
        r"cấu thành.*lượng giá trị",
        text, re.IGNORECASE
    ))
    if has_formula:
        formula_qs.append(q)

print(f"Found {len(formula_qs)} formula questions:")
for q in formula_qs:
    print(f"\nQ{q['id']}: {q['question'][:150]}")
    opts_str = ' | '.join([f"{k}: {v[:60]}" for k, v in q.get('options', {}).items()])
    print(f"   Opts: {opts_str}")
    print(f"   Current type: {q.get('type')}")
