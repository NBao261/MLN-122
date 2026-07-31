import re
import json

with open(r"c:\Users\Admin\Desktop\MLN122\extracted_text.txt", "r", encoding="utf-8") as f:
    full_text = f.read()

# Remove page markers and join lines
full_text = re.sub(r'\r\n', '\n', full_text)
full_text = re.sub(r'\n===== PAGE \d+ =====\n', '\n', full_text)

# Split into blocks - each question block ends before the next question starts
# Pattern: question text, then options (A., B., C., D.), then answer letter(s)
# We'll parse by finding answer patterns

lines = full_text.split('\n')

questions = []
current_block = []
current_question = None

def parse_block(block_lines):
    """Parse a block of lines into a question dict"""
    if not block_lines:
        return None
    
    text = '\n'.join(block_lines).strip()
    if not text:
        return None
    
    # Find options pattern
    # Options start with A., A ., B., B ., etc.
    option_pattern = r'^([A-D])\s*[\.\)]\s*(.+?)$'
    
    # Find answer line - standalone letter(s) like "A", "B", "C", "D", "AB", "AC", "ABC", etc.
    answer_pattern = r'^([A-Da-d]{1,4})$'
    
    # Parse the block
    question_lines = []
    options = {}
    current_option = None
    current_option_text = []
    answer = None
    explanation_lines = []
    in_explanation = False
    
    i = 0
    while i < len(block_lines):
        line = block_lines[i].strip()
        
        if not line:
            i += 1
            continue
        
        # Check if this is an answer line (standalone letter(s))
        answer_match = re.match(answer_pattern, line)
        if answer_match and current_option is not None:
            # This is the answer
            if current_option and current_option_text:
                options[current_option] = ' '.join(current_option_text).strip()
            answer = answer_match.group(1).upper()
            in_explanation = True
            i += 1
            continue
        
        if in_explanation:
            explanation_lines.append(line)
            i += 1
            continue
        
        # Check if this is an option line
        opt_match = re.match(option_pattern, line)
        if opt_match:
            # Save previous option
            if current_option and current_option_text:
                options[current_option] = ' '.join(current_option_text).strip()
            current_option = opt_match.group(1)
            current_option_text = [opt_match.group(2).strip()]
            i += 1
            continue
        
        # If we're in an option, this is continuation text
        if current_option is not None:
            current_option_text.append(line)
        else:
            # This is question text
            question_lines.append(line)
        
        i += 1
    
    # Save last option
    if current_option and current_option_text:
        options[current_option] = ' '.join(current_option_text).strip()
    
    if not question_lines or not options or not answer:
        return None
    
    question_text = ' '.join(question_lines).strip()
    # Clean up source markers like (NHUNG HOÀNG), (073-356-8678)
    question_text = re.sub(r'\(NHUNG\s*HOÀNG\)', '', question_text)
    question_text = re.sub(r'\(073-356-8678\)', '', question_text)
    question_text = question_text.strip()
    
    explanation = ' '.join(explanation_lines).strip() if explanation_lines else ""
    # Clean explanation - remove "Kiểu hỏi khác" blocks that are alternative question forms
    if explanation.startswith('(Kiểu hỏi khác'):
        explanation = ""
    
    return {
        'question': question_text,
        'options': options,
        'answer': answer,
        'explanation': explanation
    }


# Strategy: Find questions by looking for option A patterns and working backwards
# A question starts with non-option text, followed by A., B., C./D., then answer

# Let's use a different approach - split by answer patterns
# Find all lines that are just a letter answer (A, B, C, D, AB, AC, etc.)
answer_indices = []
for i, line in enumerate(lines):
    stripped = line.strip()
    if re.match(r'^[A-Da-d]{1,4}$', stripped) and stripped:
        # Verify this looks like an answer (preceded by option lines)
        # Look back for option patterns
        has_options = False
        for j in range(max(0, i-20), i):
            if re.match(r'^\s*[A-D]\s*[\.\)]', lines[j]):
                has_options = True
                break
        if has_options:
            answer_indices.append(i)

# Now find question boundaries
# Each question ends at an answer line
# The next question starts after the answer line (+ optional explanation)
question_blocks = []

for idx, ans_idx in enumerate(answer_indices):
    # Find the start of this question
    if idx == 0:
        start = 0
    else:
        # Start after the previous answer line
        prev_ans = answer_indices[idx - 1]
        start = prev_ans + 1
        # Skip explanation lines (lines starting with '(' or empty lines)
        while start < ans_idx and (not lines[start].strip() or lines[start].strip().startswith('(')):
            start += 1
    
    # Include answer line
    end = ans_idx
    
    # Also include explanation after answer
    explanation_end = end + 1
    while explanation_end < len(lines) and lines[explanation_end].strip().startswith('('):
        # Find closing paren
        while explanation_end < len(lines) and ')' not in lines[explanation_end]:
            explanation_end += 1
        explanation_end += 1
    
    block = lines[start:explanation_end]
    question_blocks.append(block)

# Parse all blocks
parsed_questions = []
for block in question_blocks:
    q = parse_block(block)
    if q and len(q['options']) >= 2:
        parsed_questions.append(q)

# Deduplicate by question text (fuzzy)
seen = set()
unique_questions = []
for q in parsed_questions:
    key = re.sub(r'\s+', ' ', q['question'][:80]).strip().lower()
    if key not in seen:
        seen.add(key)
        unique_questions.append(q)

# Add IDs
for i, q in enumerate(unique_questions):
    q['id'] = i + 1

print(f"Total questions parsed: {len(unique_questions)}")

# Save as JSON
with open(r"c:\Users\Admin\Desktop\MLN122\questions.json", "w", encoding="utf-8") as f:
    json.dump(unique_questions, f, ensure_ascii=False, indent=2)

# Print sample
for q in unique_questions[:5]:
    print(f"\n--- Q{q['id']} ---")
    print(f"Q: {q['question'][:100]}")
    for k, v in q['options'].items():
        print(f"  {k}. {v[:60]}")
    print(f"Answer: {q['answer']}")
    if q['explanation']:
        print(f"Note: {q['explanation'][:80]}")
