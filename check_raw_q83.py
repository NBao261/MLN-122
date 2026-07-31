import json

with open('extracted_text.txt', 'r', encoding='utf-8') as f:
    text = f.read()

# Search for Q83 & Q84 text in extracted_text.txt
idx = text.find('Để sản xuất ra 1000 đối dép')
if idx != -1:
    print(text[idx:idx+1000])
