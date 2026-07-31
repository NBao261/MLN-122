import json

with open('extracted_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

idx = text.find('Gọi W là giá trị hàng hóa')
if idx != -1:
    print(text[idx-200:idx+500])
