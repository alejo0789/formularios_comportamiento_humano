import pdfplumber
import re
from typing import Dict, Any, List, Optional
import os

class PDFService:
    def __init__(self):
        pass

    async def extract_text_from_pdf(self, file_path: str) -> Dict[str, Any]:
        """
        Extracts text and basic structure from a PDF file.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"PDF file not found: {file_path}")

        extracted_data = {
            "full_text": "",
            "pages": [],
            "metadata": {},
            "potential_form_fields": []
        }

        try:
            with pdfplumber.open(file_path) as pdf:
                # Extract metadata
                extracted_data["metadata"] = pdf.metadata

                for i, page in enumerate(pdf.pages):
                    raw_text = page.extract_text() or ""
                    
                    # Clean text using helper method
                    page_text = self._clean_text(raw_text)
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    
                    # Basic form field detection (checkboxes, underlines)
                    # This is a heuristic approach
                    form_fields = self._detect_form_elements(page)
                    
                    page_data = {
                        "page_number": i + 1,
                        "text": page_text,
                        "tables": tables,
                        "form_fields": form_fields
                    }
                    
                    extracted_data["pages"].append(page_data)
                    extracted_data["full_text"] += page_text + "\n\n"
                    extracted_data["potential_form_fields"].extend(form_fields)

        except Exception as e:
            print(f"Error extraction PDF: {str(e)}")
            raise e

        return extracted_data

    def _clean_text(self, text: str) -> str:
        """
        Cleans text from common PDF extraction artifacts like encoding errors.
        """
        if not text:
            return ""
            
        # Remove replacement characters () often seen in bad encodings
        text = text.replace('\ufffd', '')
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Sometimes text comes as "T e x t" due to layout spacing
        # If density of spaces is too high (e.g. > 40% of chars are spaces in a wordy line), 
        # it might be spaced text. 
        # For now, simple replacement of double spaces to single
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()

    def _detect_form_elements(self, page) -> List[Dict[str, Any]]:
        """
        Heuristic detection of form elements like checkboxes and underlined spaces.
        """
        elements = []
        
        # Check for rectangles (potential checkboxes)
        rects = page.rects
        for rect in rects:
            # Filter distinctively small rectangles often used for checkboxes
            if 5 < rect['width'] < 30 and 5 < rect['height'] < 30:
                elements.append({
                    "type": "checkbox",
                    "bbox": (rect['x0'], rect['top'], rect['x1'], rect['bottom']),
                    "page": page.page_number
                })

        # Check for lines (potential text inputs)
        lines = page.lines
        for line in lines:
            # Filter horizontal lines
            if line['width'] > 50 and abs(line['y0'] - line['y1']) < 2:
                 elements.append({
                    "type": "text_input",
                    "bbox": (line['x0'], line['top'], line['x1'], line['bottom']),
                    "page": page.page_number
                })
                
        return elements

    def analyze_structure(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes the extracted text to guess the type of document and its sections.
        """
        text = extracted_data["full_text"]
        
        structure = {
            "document_type": "unknown",
            "title": "",
            "sections": [],
            "questions": [] # Attempt to parse questions
        }

        # 1. Guess Title (First few lines)
        lines = text.split('\n')
        # Filter very short lines or just dates which often appear first in headers
        non_empty_lines = [l.strip() for l in lines if len(l.strip()) > 3 and not l.strip().startswith("Fecha")]
        
        if non_empty_lines:
            # Better title detection: look for shortest meaningful uppercase line in first few lines
            for line in non_empty_lines[:8]:
                 clean_line = line.strip()
                 if len(clean_line) > 5 and len(clean_line) < 100 and clean_line.isupper():
                     structure["title"] = clean_line
                     break
            if not structure["title"] and non_empty_lines:
                 structure["title"] = non_empty_lines[0][:100] # Fallback but limit length

        # 2. Key phrases for document type
        lower_text = text.lower()
        if "evaluaci" in lower_text or "cuestionario" in lower_text or "encuesta" in lower_text:
            structure["document_type"] = "questionnaire"
        elif "formato" in lower_text or "ficha" in lower_text:
             structure["document_type"] = "form"
        
        # 3. Improved Question Extraction
        # In specific PDF (like "Cuestionario estres"), text extraction might merge lines.
        # We need to look for "NUMBER. Text" pattern deeply.
        
        potential_questions = []
        
        # Regex to find embedded questions like "1. Question. 2. Other"
        # It looks for a number, a dot, space, some text, until next number dot space or end
        matches = re.finditer(r'(\d+\.)\s+([^0-9]+?)(?=\s*\d+\.|\Z)', text, re.DOTALL)
        
        for match in matches:
            q_num = match.group(1)
            q_text = match.group(2).strip()
            # Filter valid questions (length check)
            if len(q_text) > 5:
                potential_questions.append(f"{q_num} {q_text}")
                
        # Fallback to line-by-line if regex didn't find much (maybe format is different)
        if len(potential_questions) < 2:
             for line in non_empty_lines:
                if re.match(r'^\d+[\.)]\s+', line) or re.match(r'^[a-z][\.)]\s+', line):
                    potential_questions.append(line)
                elif "?" in line or "¿" in line:
                    potential_questions.append(line)

        structure["questions"] = potential_questions[:30] # Limit increase
        
        return structure
