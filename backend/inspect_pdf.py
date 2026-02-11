import pypdf
import os

pdf_path = r"c:\Users\alejandro.carvajal\Documents\Formularios\Bateria de RX Psicosocial 2024 (1).pdf"

def detailed_inspect(path):
    if not os.path.exists(path):
        print(f"File not found: {path}")
        return
    
    with open(path, "rb") as f:
        reader = pypdf.PdfReader(f)
        num_pages = len(reader.pages)
        print(f"Total pages: {num_pages}")
        
        for i in range(num_pages):
            text = reader.pages[i].extract_text()
            lines = text.split('\n')
            
            # Print page number and header info
            header = " | ".join([line.strip() for line in lines[:5] if line.strip()])
            print(f"Page {i+1}: {header[:200]}")
            
            text_lower = text.lower()
            if "bajo" in text_lower and "alto" in text_lower:
                 print(f"  -> Likely Data/Table Page Found")
            
            if "dominio" in text_lower:
                 print(f"  -> Mentions DOMINIO")
            
            if "dimensi" in text_lower:
                 print(f"  -> Mentions DIMENSION")

if __name__ == "__main__":
    detailed_inspect(pdf_path)
