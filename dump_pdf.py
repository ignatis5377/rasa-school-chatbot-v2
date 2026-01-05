import sys
from pypdf import PdfReader

def dump_text(pdf_path, out_path):
    try:
        reader = PdfReader(pdf_path)
        with open(out_path, 'w', encoding='utf-8') as f:
            for page in reader.pages:
                text = page.extract_text()
                f.write(text)
                f.write("\n--- PAGE BREAK ---\n")
        print(f"Successfully wrote text to {out_path}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    dump_text('files_to_upload/MATH_EASY_1.pdf', 'debug_pdf_text.txt')
