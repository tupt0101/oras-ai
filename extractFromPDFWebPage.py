import io

import requests
import re
from PyPDF2 import PdfFileReader

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