import fitz  # PyMuPDF
from typing import List, Dict, Any
import os
from datetime import datetime
from tqdm.auto import tqdm
class PDFProcessor:
    def __init__(self):
        """Initialize PDF processor."""
        self.chunk_size = 1000  # Number of characters per chunk
        self.chunk_overlap = 200  # Number of characters to overlap between chunks

    def text_formatter(self, text):
        clean_text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
        return clean_text

    def extract_text_from_pdf(self,pdf_path):
        doc = fitz.open(pdf_path)
        page_and_text = []
        for page_number, page in tqdm(enumerate(doc)):
            text = page.get_text()
            text = self.text_formatter(text)
            page_and_text.append({
                'text': text,
                'metadata': {
                    'page_number': page_number,
                    'page_char_count': len(text),
                    'page_word_count': len(text.split()),
                    'page_sentence_count': len(text.split('.')),
                    'page_token_count': len(text) / 4,
            }})
            
        return page_and_text

    def process_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """Process PDF file and return chunks with metadata."""
        try:
            chunks = self.extract_text_from_pdf(pdf_path)
            return chunks
        except Exception as e:
            raise Exception(f"Error processing PDF: {str(e)}") 



if __name__ == "__main__":
    pdf_processor = PDFProcessor()
    pdf_path = "/Users/tringuyen1803/Documents/RAG/model/meta.pdf"
    chunks = pdf_processor.process_pdf(pdf_path)
    print(chunks[:1])