"""
MLN122 PDF Parser v2 - Complete rewrite
Handles all option formats: A., a., A), a), a .
Properly separates "Kiểu hỏi khác" blocks
Ensures no questions are lost
"""
import re
import json

with open(r"c:\Users\Admin\Desktop\MLN122\extracted_text.txt", "r", encoding="utf-8") as f:
    raw = f.read()

# Normalize line endings
raw = raw.replace('\r\n', '\n').replace('\r', '\n')

# Remove page markers
raw = re.sub(r'\n===== PAGE \d+ =====\n', '\n', raw)

# Remove the Quizlet header (first few lines)
raw = re.sub(r'^MLN122 - CHUẨN NHUNG HOÀNG.*?Nhóm\n', '', raw, flags=re.DOTALL)

lines = raw.split('\n')

# ============================================================
# STRATEGY: Find answer lines, then work backwards to find 
# the question+options block above each answer.
# 
# Answer line patterns: standalone letter(s) on a line
#   "A", "B", "C", "D", "a", "b", "c", "d"
#   "AB", "AC", "ABC", "ABD", etc.
# ============================================================

# Option line patterns (covers all formats in the PDF)
OPTION_PATTERNS = [
    r'^([A-Da-d])\s*[\.\)]\s*(.+)',       # A. text, A) text, a. text, a) text
    r'^([A-Da-d])\s*\.\s*(.+)',            # A . text  
]

def is_option_line(line):
    """Check if a line starts an option (A., B., a), etc.)"""
    stripped = line.strip()
    for pat in OPTION_PATTERNS:
        if re.match(pat, stripped):
            return True
    return False

def get_option_letter(line):
    """Extract option letter from line"""
    stripped = line.strip()
    for pat in OPTION_PATTERNS:
        m = re.match(pat, stripped)
        if m:
            return m.group(1).upper(), m.group(2).strip()
    return None, None

def is_answer_line(line):
    """Check if a line is a standalone answer (A, B, C, D, a, b, c, d, AB, AC, etc.)"""
    stripped = line.strip()
    if not stripped:
        return False
    # Must be 1-4 letters, all A-D
    if re.match(r'^[A-Da-d]{1,4}$', stripped):
        return True
    return False

def is_noise_line(line):
    """Check if line is noise (page markers, source tags, etc.)"""
    stripped = line.strip()
    if not stripped:
        return True
    # Quizlet UI elements
    if stripped in ['Lưu', 'Nhóm', 'SOURCE']:
        return True
    return False

def clean_question_text(text):
    """Remove source markers and noise from question text"""
    text = re.sub(r'\(NHUNG\s*HOÀNG\)', '', text)
    text = re.sub(r'\(073[-\s]*356[-\s]*8678\)', '', text)
    text = text.strip()
    return text

# ============================================================
# PASS 1: Find all answer line positions
# ============================================================
answer_positions = []
for i, line in enumerate(lines):
    if is_answer_line(line.strip()):
        answer_positions.append(i)

print(f"Found {len(answer_positions)} potential answer lines")

# ============================================================
# PASS 2: For each answer line, scan backwards to find options
# and question text. Build question blocks.
# ============================================================
questions = []
used_lines = set()  # Track which lines have been consumed

for ans_idx in answer_positions:
    answer = lines[ans_idx].strip().upper()
    
    # Scan backwards from answer line to find options
    options = {}
    option_start_lines = []
    
    i = ans_idx - 1
    # Collect option lines going backwards
    option_blocks = []  # [(letter, start_line, lines_list)]
    current_opt_letter = None
    current_opt_lines = []
    
    while i >= 0:
        line = lines[i].strip()
        
        if not line:
            i -= 1
            continue
            
        letter, text = get_option_letter(lines[i])
        
        if letter:
            # This starts a new option
            if current_opt_letter:
                option_blocks.append((current_opt_letter, current_opt_lines[::-1]))
            current_opt_letter = letter
            current_opt_lines = [text]
            option_start_lines.append(i)
            i -= 1
            continue
        
        if current_opt_letter:
            # Check if this is a continuation of the current option
            # or if we've hit the question text
            # Heuristic: if we already have the option letter and this line
            # doesn't start a new option, it's either continuation or question
            
            # Check if this could be a question line (not an option continuation)
            # Options are usually short, so if we've been accumulating and hit
            # a line that doesn't look like an option continuation, stop
            if is_option_line(lines[i]):
                letter2, text2 = get_option_letter(lines[i])
                option_blocks.append((current_opt_letter, current_opt_lines[::-1]))
                current_opt_letter = letter2
                current_opt_lines = [text2]
                option_start_lines.append(i)
            else:
                current_opt_lines.append(line)
            i -= 1
            continue
        
        break
    
    # Save last option
    if current_opt_letter:
        option_blocks.append((current_opt_letter, current_opt_lines[::-1]))
    
    if len(option_blocks) < 2:
        continue  # Not a valid question (need at least 2 options)
    
    # Reverse option_blocks since we collected them backwards
    option_blocks.reverse()
    option_start_lines.reverse()
    
    # Build options dict
    for letter, opt_lines in option_blocks:
        options[letter] = ' '.join(opt_lines).strip()
    
    # Validate answer: must match one of the options (or combination)
    valid_answer = True
    for ch in answer:
        if ch not in options:
            valid_answer = False
            break
    
    if not valid_answer:
        continue
    
    # Find question text: everything between previous answer/question end
    # and the first option line
    first_option_line = min(option_start_lines) if option_start_lines else ans_idx
    
    # Go backwards from first option to find question text
    q_lines = []
    j = first_option_line - 1
    while j >= 0:
        line = lines[j].strip()
        if not line:
            j -= 1
            continue
        
        # Stop if we hit a previous answer line
        if is_answer_line(line):
            break
        
        # Stop if we hit a "Kiểu hỏi khác" closing paren
        # These are alternative question forms that should be skipped
        if line.endswith(')') and any('Kiểu hỏi khác' in lines[k] for k in range(max(0, j-5), j+1)):
            break
        
        # Stop if line looks like closing of a parenthetical block
        # from the previous question's explanation
        if j in used_lines:
            break
            
        q_lines.append(line)
        j -= 1
    
    q_lines.reverse()
    question_text = ' '.join(q_lines).strip()
    question_text = clean_question_text(question_text)
    
    # Skip if question text is too short or empty
    if len(question_text) < 8:
        continue
    
    # Skip if question text starts with noise from previous block
    # (parenthetical explanation leaks)
    # Remove leading parenthetical noise
    question_text = re.sub(r'^[\)]\s*', '', question_text)
    question_text = re.sub(r'^[a-d]\)\s*', '', question_text)
    
    # If question starts with a lowercase letter followed by content that
    # looks like it's from a previous explanation, try to clean it
    if question_text and question_text[0].islower() and ')' in question_text[:50]:
        # Try to find the real question start after the noise
        paren_end = question_text.find(')')
        if paren_end < 50:
            remaining = question_text[paren_end+1:].strip()
            if len(remaining) > 15:
                question_text = remaining
    
    # Mark lines as used
    for li in range(j+1, ans_idx+1):
        used_lines.add(li)
    
    # Check for explanation after answer (parenthetical blocks)
    explanation = ''
    k = ans_idx + 1
    while k < len(lines):
        stripped = lines[k].strip()
        if not stripped:
            k += 1
            continue
        if stripped.startswith('(') and 'Kiểu hỏi khác' not in stripped:
            # Collect explanation
            expl_lines = []
            while k < len(lines) and (lines[k].strip().startswith('(') or (expl_lines and ')' not in ' '.join(expl_lines))):
                expl_lines.append(lines[k].strip())
                if ')' in lines[k]:
                    break
                k += 1
            explanation = ' '.join(expl_lines).strip('() ')
            # Mark as used
            for li in range(ans_idx+1, k+1):
                used_lines.add(li)
        break
    
    questions.append({
        'question': question_text,
        'options': options,
        'answer': answer,
        'explanation': explanation,
    })

print(f"Parsed {len(questions)} questions (before dedup)")

# ============================================================
# PASS 3: Clean up and deduplicate
# ============================================================
# Remove obvious duplicates (exact same question text, ignoring whitespace)
seen_questions = {}
unique = []
for q in questions:
    key = re.sub(r'\s+', ' ', q['question']).strip().lower()
    if key not in seen_questions:
        seen_questions[key] = q
        unique.append(q)
    else:
        # Keep the one with more options
        existing = seen_questions[key]
        if len(q['options']) > len(existing['options']):
            # Replace
            idx = unique.index(existing)
            unique[idx] = q
            seen_questions[key] = q

# Re-index
for i, q in enumerate(unique):
    q['id'] = i + 1

print(f"After dedup: {len(unique)} questions")

# ============================================================
# PASS 4: Final cleanup of question text
# ============================================================
final = []
for q in unique:
    text = q['question']
    
    # Remove noise patterns at start
    text = re.sub(r'^(nghiệp|vốn|điểm|như)\s+', '', text)  # truncated noise
    text = re.sub(r'^[\d]+\.\s*', '', text)  # numbered noise like "2. Phân công..."
    
    # Skip if still too short
    if len(text) < 10:
        continue
    
    q['question'] = text
    final.append(q)

# Re-index again
for i, q in enumerate(final):
    q['id'] = i + 1

print(f"Final: {len(final)} questions")

# Save
with open(r"c:\Users\Admin\Desktop\MLN122\questions_clean.json", "w", encoding="utf-8") as f:
    json.dump(final, f, ensure_ascii=False, indent=2)

# Also generate JS
js_content = 'const QUESTIONS = ' + json.dumps(final, ensure_ascii=False, indent=2) + ';'
with open(r"c:\Users\Admin\Desktop\MLN122\questions_clean.js", "w", encoding="utf-8") as f:
    f.write(js_content)

# Print samples to verify
print("\n=== SAMPLES ===")
for q in final[:5]:
    print(f"\nQ{q['id']}: {q['question'][:120]}")
    for k, v in q['options'].items():
        print(f"   {k}. {v[:80]}")
    print(f"   → Answer: {q['answer']}")

print(f"\n=== LAST 3 ===")
for q in final[-3:]:
    print(f"\nQ{q['id']}: {q['question'][:120]}")
    print(f"   → Answer: {q['answer']}")
