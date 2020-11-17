import io
import re
import requests
from docx import Document

def extractTextFromDocx(url):
    r = requests.get(url)
    f = io.BytesIO(r.content)
    document = Document(f)
    result = ' '.join([para.text for para in document.paragraphs])
    
    return re.split(r'\s{2,}', result) 