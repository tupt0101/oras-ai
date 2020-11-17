import io
import re
import requests
from PyPDF2 import PdfFileReader
from docx import Document

def extractTextFromPDF(url):
    r = requests.get(url)
    f = io.BytesIO(r.content)
    
    reader = PdfFileReader(f)
    contents = []
    for page in range(0, reader.getNumPages()):
        contents += reader.getPage(page).extractText().split('\n')
        # contents += reader.getPage(page).extractText().split('\n')
    result = ''.join(contents)
    # return contents
    return re.split(r'\s{2,}', result)

def extractTextFromDocx(url):
    r = requests.get(url)
    f = io.BytesIO(r.content)
    document = Document(f)
    result = ' '.join([para.text for para in document.paragraphs])
    
    return re.split(r'\s{2,}', result) 