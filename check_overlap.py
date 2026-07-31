import json

with open('questions_clean.json', 'r', encoding='utf-8') as f:
    qs = json.load(f)

alt_questions = [
    'Khi nghiên cứu về cách mạng công nghiệp lần thứ nhất',
    'Cách mạng công nghiệp lần thứ hai diễn ra',
    'Nguồn gốc nào không đúng với nguồn vốn công nghiệp hóa',
    'phương pháp sản xuất giá trị thặng dư tuyệt đối',
    'Kinh tế chính trị cổ điển Anh được hình thành',
    'Cách mạng công nghiệp lần thứ ba diễn ra',
    'Xuất khẩu hàng hóa là một trong những đặc điểm',
    'lấy thị trường làm phương tiện',
    'Tích lũy tư bản là gì',
    'người đầu tiên đưa ra khái niệm',
    'Hàng hóa là gì',
    'xuất khẩu tư bản nhà nước thường hướng vào',
]

overlap_count = 0
unique_count = 0
for alt in alt_questions:
    matches = [q for q in qs if alt.lower() in q['question'].lower()]
    if matches:
        overlap_count += 1
        print(f'OVERLAP: "{alt[:60]}..."')
        for m in matches:
            print(f'  -> Q{m["id"]}: {m["question"][:100]}')
    else:
        unique_count += 1
        print(f'UNIQUE:  "{alt[:60]}..."')
    print()

print(f"\nSummary: {overlap_count} overlap with existing, {unique_count} are truly unique")
print(f"Current total: {len(qs)} questions")
print(f"PDF header claims: 517 questions")
print(f"Gap: {517 - len(qs)} questions")
