import PyPDF2
import docx

def extract_text_from_pdf(pdf_path):
    with open(pdf_path, "rb") as file:
        reader = PyPDF2.PdfReader(file)
        text = "".join([page.extract_text() for page in reader.pages])
        return text

def extract_text_from_docx(docx_path):
    doc = docx.Document(docx_path)
    return "\n".join([para.text for para in doc.paragraphs])

def combine_file(text_content, signature, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("--- Nội dung văn bản ---\n")
        f.write(text_content.strip() + "\n")
        f.write("--- Chữ ký ---\n")
        f.write(f"{signature[0]},{signature[1]}")

def split_combined_file(combined_file):
    with open(combined_file, "r", encoding="utf-8") as f:
        content = f.read()
    parts = content.split("--- Chữ ký ---")
    if len(parts) != 2:
        raise ValueError("File tổng hợp không đúng định dạng!")
    text_content = parts[0].replace("--- Nội dung văn bản ---", "").strip()
    signature_parts = parts[1].strip().split(",")
    signature = (int(signature_parts[0]), int(signature_parts[1]))
    return text_content, signature