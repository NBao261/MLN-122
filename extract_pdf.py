import fitz  # PyMuPDF
import sys

pdf_path = r"c:\Users\Admin\Desktop\MLN122\Thẻ ghi nhớ_ MLN122 - CHUẨN NHUNG HOÀNG _ Quizlet.pdf"

doc = fitz.open(pdf_path)
full_text = ""
for page_num in range(len(doc)):
    page = doc[page_num]
    text = page.get_text("text")
    full_text += f"\n===== PAGE {page_num + 1} =====\n"
    full_text += text

with open(r"c:\Users\Admin\Desktop\MLN122\extracted_text.txt", "w", encoding="utf-8") as f:
    f.write(full_text)

print(f"Extracted {len(doc)} pages")
print("First 5000 chars:")
print(full_text[:5000])
