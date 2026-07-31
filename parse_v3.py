"""
MLN122 PDF Parser v3 - Forward scanning approach
Splits text into question blocks using answer lines as delimiters.
Handles: A., a., A), a), A . formats
Skips: (Kiểu hỏi khác ...) blocks
"""
import re
import json

with open(r"extracted_text.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Normalize
raw = raw.replace('\r\n', '\n').replace('\r', '\n')
# Remove page markers
raw = re.sub(r'\n===== PAGE \d+ =====\n', '\n', raw)
lines = raw.split('\n')

# ============================================================
# STEP 1: Remove "Kiểu hỏi khác" blocks (they are in parentheses)
# These are alternative question forms that mess up parsing
# ============================================================
clean_lines = []
in_kieu_hoi = False
paren_depth = 0

for line in lines:
    stripped = line.strip()
    
    if '(Kiểu hỏi khác' in stripped or '( Kiểu hỏi khác' in stripped:
        in_kieu_hoi = True
        paren_depth = stripped.count('(') - stripped.count(')')
        continue
    
    if in_kieu_hoi:
        paren_depth += stripped.count('(') - stripped.count(')')
        if paren_depth <= 0 or stripped.endswith(')'):
            in_kieu_hoi = False
        continue
    
    clean_lines.append(stripped)

print(f"Lines after removing Kiểu hỏi khác: {len(clean_lines)} (from {len(lines)})")

# ============================================================
# STEP 2: Remove noise lines at the very beginning
# ============================================================
# Skip the Quizlet header
start_idx = 0
for i, line in enumerate(clean_lines):
    if line == 'Nhóm':
        start_idx = i + 1
        break

clean_lines = clean_lines[start_idx:]

# ============================================================
# STEP 3: Join multi-line text into single lines where needed
# We'll work with a flat text and re-split by answer markers
# ============================================================

# An answer line is a standalone line with 1-4 letters A-D (case insensitive)
ANSWER_RE = re.compile(r'^[A-Da-d]{1,4}$')

# Option start patterns
OPT_RE = re.compile(r'^([A-Da-d])\s*[\.\)]\s*(.+)')
# Special case: "A . text" (space before dot)
OPT_RE2 = re.compile(r'^([A-Da-d])\s+\.\s*(.+)')

def is_answer(s):
    return bool(ANSWER_RE.match(s.strip()))

def parse_option(s):
    """Try to parse an option line. Returns (letter, text) or None."""
    s = s.strip()
    m = OPT_RE.match(s)
    if m:
        return m.group(1).upper(), m.group(2).strip()
    m = OPT_RE2.match(s)
    if m:
        return m.group(1).upper(), m.group(2).strip()
    return None

# ============================================================
# STEP 4: Split into raw blocks delimited by answer lines
# A block = question text + options + answer line
# ============================================================
blocks = []
current_block_lines = []

for line in clean_lines:
    stripped = line.strip()
    if not stripped:
        continue
    
    # Skip noise
    if stripped in ['Lưu', 'Nhóm', 'SOURCE']:
        continue
    
    if is_answer(stripped):
        if current_block_lines:
            blocks.append({
                'lines': current_block_lines,
                'answer': stripped.upper()
            })
            current_block_lines = []
        continue
    
    current_block_lines.append(stripped)

print(f"Found {len(blocks)} raw blocks")

# ============================================================
# STEP 5: Parse each block into question + options
# ============================================================
questions = []

for block in blocks:
    block_lines = block['lines']
    answer = block['answer']
    
    # Find where options start
    # Scan forward to find the first option line
    first_opt_idx = None
    for i, line in enumerate(block_lines):
        parsed = parse_option(line)
        if parsed:
            first_opt_idx = i
            break
    
    if first_opt_idx is None:
        # No options found - skip
        continue
    
    # Question text = everything before first option
    q_lines = block_lines[:first_opt_idx]
    question_text = ' '.join(q_lines).strip()
    
    # Parse options
    options = {}
    current_letter = None
    current_text_parts = []
    
    for line in block_lines[first_opt_idx:]:
        parsed = parse_option(line)
        if parsed:
            # Save previous option if any
            if current_letter:
                options[current_letter] = ' '.join(current_text_parts).strip()
            current_letter = parsed[0]
            current_text_parts = [parsed[1]]
        else:
            # Continuation of current option
            if current_letter:
                current_text_parts.append(line.strip())
    
    # Save last option
    if current_letter:
        options[current_letter] = ' '.join(current_text_parts).strip()
    
    # Validate
    if len(options) < 2:
        continue
    
    # Check answer matches options
    valid = True
    for ch in answer:
        if ch not in options:
            valid = False
            break
    if not valid:
        continue
    
    # Clean question text
    question_text = re.sub(r'\(NHUNG\s*HOÀNG\)', '', question_text)
    question_text = re.sub(r'\(073[-\s]*356[-\s]*8678\)', '', question_text)
    question_text = re.sub(r'\s+', ' ', question_text).strip()
    
    # Remove trailing colons, question marks cleanup
    question_text = question_text.strip()
    
    if len(question_text) < 5:
        continue
    
    questions.append({
        'question': question_text,
        'options': options,
        'answer': answer,
        'explanation': '',
    })

print(f"Parsed {len(questions)} questions (before dedup)")

# ============================================================
# STEP 6: Detect and fix questions where previous question's
# options leaked into the current question text
# 
# Pattern: question text contains "a) ... b) ... c) ... d) ..."
# which are actually options from a different question format
# ============================================================
fixed_questions = []
for q in questions:
    text = q['question']
    
    # Check if question text contains inline options like "a) text b) text"
    # These are from questions that use a different format
    inline_opts = re.findall(r'[a-dA-D]\)\s*[^a-dA-D\)]+', text)
    
    if len(inline_opts) >= 3:
        # This question text contains inline options from a previous merged question
        # Try to split: find where the REAL question starts
        # The real question is typically after the last inline option group
        
        # Find the last occurrence of "d)" or "c)" followed by text, 
        # then the real question starts after
        last_opt_match = None
        for m in re.finditer(r'[a-dA-D]\)\s*[^a-dA-D\)]+', text):
            last_opt_match = m
        
        if last_opt_match:
            # Everything after the last inline option is the real question
            remainder = text[last_opt_match.end():].strip()
            if len(remainder) >= 10:
                q['question'] = remainder
            else:
                # The whole thing might be two merged questions
                # Just try to find a sentence that looks like a question
                # after the options block
                pass
    
    fixed_questions.append(q)

questions = fixed_questions

# ============================================================
# STEP 7: Deduplicate
# ============================================================
seen = {}
unique = []
for q in questions:
    key = re.sub(r'\s+', '', q['question']).lower()
    if key not in seen:
        seen[key] = True
        unique.append(q)

print(f"After dedup: {len(unique)} questions")

# Re-index
for i, q in enumerate(unique):
    q['id'] = i + 1

# Save JSON
with open(r"questions_clean.json", "w", encoding="utf-8") as f:
    json.dump(unique, f, ensure_ascii=False, indent=2)

# Save JS
js = 'const QUESTIONS = ' + json.dumps(unique, ensure_ascii=False, indent=2) + ';'
with open(r"questions_clean.js", "w", encoding="utf-8") as f:
    f.write(js)

print(f"\n✅ Final: {len(unique)} questions saved")

# ============================================================
# Verify: print some samples
# ============================================================
print("\n=== FIRST 5 QUESTIONS ===")
for q in unique[:5]:
    print(f"\nQ{q['id']}: {q['question'][:150]}")
    for k, v in sorted(q['options'].items()):
        marker = " ✅" if k in q['answer'] else ""
        print(f"   {k}. {v[:100]}{marker}")
    print(f"   Answer: {q['answer']}")

print("\n=== LAST 3 QUESTIONS ===")
for q in unique[-3:]:
    print(f"\nQ{q['id']}: {q['question'][:150]}")
    for k, v in sorted(q['options'].items()):
        marker = " ✅" if k in q['answer'] else ""
        print(f"   {k}. {v[:100]}{marker}")
    print(f"   Answer: {q['answer']}")

# Check for potentially problematic questions (inline options in question text)
print("\n=== QUESTIONS WITH POTENTIAL ISSUES (inline options in text) ===")
issues = 0
for q in unique:
    text = q['question']
    if re.search(r'[a-d]\)\s*.+[a-d]\)\s*.+[a-d]\)', text):
        issues += 1
        if issues <= 5:
            print(f"\n⚠️ Q{q['id']}: {text[:200]}")
print(f"\nTotal potentially problematic: {issues}")
