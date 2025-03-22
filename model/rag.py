import fitz
from tqdm.auto import tqdm

def text_formatter(text):
    clean_text = text.replace('\n', ' ').replace('\r', ' ').replace('\t', ' ')
    return clean_text

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    text = ''
    for page in tqdm(doc, desc='Extracting text from PDF'):
        text += page.get_text()
    return text_formatter(text)

page_and_text = extract_text_from_pdf('meta.pdf')
page_and_text