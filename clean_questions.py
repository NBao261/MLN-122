import json
import re

with open(r"c:\Users\Admin\Desktop\MLN122\questions.json", "r", encoding="utf-8") as f:
    questions = json.load(f)

cleaned = []
for q in questions:
    text = q['question']
    
    # Skip questions with garbage/truncated text
    if len(text) < 15:
        continue
    
    # Clean leading noise from explanation leaks
    # Remove patterns like "điểm gì?) ", "như thế nào?) ", "vốn công nghiệp...) "
    text = re.sub(r'^[^A-ZĐÀÁẢÃẠĂẮẰẲẴẶÂẤẦẨẪẬÈÉẺẼẸÊẾỀỂỄỆÌÍỈĨỊÒÓỎÕỌÔỐỒỔỖỘƠỚỜỞỠỢÙÚỦŨỤƯỨỪỬỮỰỲÝỶỸỴ"\']+', '', text)
    text = text.strip()
    
    if len(text) < 15:
        continue
    
    # Remove Quizlet header from first question
    text = re.sub(r'MLN122 - CHUẨN NHUNG HOÀNG.*?Nhóm\s*', '', text)
    
    # Clean remaining source markers
    text = re.sub(r'\(NHUNG\s*HOÀNG\)', '', text)
    text = re.sub(r'\(073[-\s]*356[-\s]*8678\)', '', text)
    text = text.strip()
    
    # Clean explanation - remove alternative question forms
    explanation = q.get('explanation', '')
    if explanation and ('Kiểu hỏi khác' in explanation or 'Hoạt động nào' in explanation):
        explanation = ''
    
    # Skip if question text is too similar to noise
    if text.startswith('2. Phân công') or text.startswith('và là cơ sở'):
        continue
    if text.startswith('nghiệp lần thứ nhất'):
        continue
    
    q['question'] = text
    q['explanation'] = explanation
    cleaned.append(q)

# Re-index
for i, q in enumerate(cleaned):
    q['id'] = i + 1

# Final output
print(f"Cleaned questions: {len(cleaned)}")

with open(r"c:\Users\Admin\Desktop\MLN122\questions_clean.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, ensure_ascii=False, indent=2)

# Verify some samples
for q in cleaned[:3]:
    print(f"\nQ{q['id']}: {q['question'][:120]}")
    print(f"   Answer: {q['answer']}")
