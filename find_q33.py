"""
Find the source text for Q33 in extracted_text.txt
"""

with open('extracted_text.txt', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Search for context around "Tien cong thuc te la"
search_terms = ['Tích tụ và tập trung tư bản', 'Tiền công thực tế là', 'Phân công lao động xã hội']

for term in search_terms:
    print(f"\n=== Searching for: '{term}' ===")
    for i, line in enumerate(lines):
        if term in line:
            start = max(0, i-5)
            end = min(len(lines), i+10)
            print(f"Found at line {i}:")
            for j in range(start, end):
                print(f"  [{j}]: {lines[j].rstrip()}")
            print("---")
