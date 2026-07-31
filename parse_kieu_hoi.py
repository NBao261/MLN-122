"""
Parse 'Kiểu hỏi khác' blocks and merge them into the main question set
"""
import re, json

with open('extracted_text.txt', 'r', encoding='utf-8') as f:
    raw = f.read()

raw = raw.replace('\r\n', '\n').replace('\r', '\n')

# Extract all Kiểu hỏi khác blocks
blocks = list(re.finditer(r'\(Kiểu hỏi khác[:\s]*(.+?)\)', raw, re.DOTALL))

OPT_RE = re.compile(r'([A-Da-d])\s*[\.\)]\s*(.+?)(?=(?:[A-Da-d]\s*[\.\)])|$)', re.DOTALL)

parsed = []
for m in blocks:
    content = m.group(1).strip()
    content = re.sub(r'\s+', ' ', content)
    
    # Try to find options
    opts_matches = list(OPT_RE.finditer(content))
    
    if len(opts_matches) >= 2:
        question = content[:opts_matches[0].start()].strip().rstrip(':').strip()
        options = {}
        for om in opts_matches:
            letter = om.group(1).upper()
            text = om.group(2).strip()
            options[letter] = text
        
        # Check for embedded answer (=> or ->)
        answer = ''
        for key, val in list(options.items()):
            if '=>' in val or '->' in val:
                answer = key
                options[key] = re.sub(r'[=\->].*', '', val).strip()
        
        if not answer:
            answer = '?'
        
        if question and len(options) >= 2:
            parsed.append({
                'question': question,
                'options': options,
                'answer': answer,
            })
    else:
        # No structured options - might have => answer inline
        if '=>' in content or '->' in content:
            parts = re.split(r'[=\-]>', content, maxsplit=1)
            question = parts[0].strip().rstrip(':').strip()
            answer_text = parts[1].strip() if len(parts) > 1 else ''
            if question and answer_text:
                parsed.append({
                    'question': question,
                    'options': {},
                    'answer': '?',
                    'answer_text': answer_text,
                })
        else:
            # Question only, no options
            parsed.append({
                'question': content.strip(),
                'options': {},
                'answer': '?',
            })

print(f"Parsed {len(parsed)} Kiểu hỏi khác blocks")
print()

# Show details
with_options = [p for p in parsed if len(p.get('options', {})) >= 2]
without_options = [p for p in parsed if len(p.get('options', {})) < 2]

print(f"  With options (can be added as quiz): {len(with_options)}")
print(f"  Without structured options: {len(without_options)}")
print()

for i, p in enumerate(with_options):
    print(f"--- With Options #{i+1} ---")
    q = p['question']
    print(f"  Q: {q[:200]}")
    for k, v in sorted(p['options'].items()):
        print(f"     {k}. {v[:100]}")
    print(f"  Answer: {p['answer']}")
    print()

print("===== WITHOUT OPTIONS =====")
for i, p in enumerate(without_options):
    print(f"--- #{i+1} ---")
    q = p['question']
    print(f"  Q: {q[:200]}")
    if p.get('answer_text'):
        print(f"  => {p['answer_text'][:150]}")
    print()
