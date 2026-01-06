import os
from pypdf import PdfReader

# Path to PDF
pdf_path = r"C:\Users\alejandro.carvajal\Documents\Formularios\pdf\Formulario-Clima-Organizacional.pdf"

try:
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    
    print("--- START PDF CONTENT ---")
    print(text)
    print("--- END PDF CONTENT ---")

except Exception as e:
    print(f"Error extracting text: {e}")
