import json

from flask import Flask, request

from textConvertor import convertPDFToText, convertDocxToText
from textExtraction import extractTextFromPDF, extractTextFromDocx
from textProcessor import processJD, processResume
from textCalculator import calcSimilar

app = Flask(__name__)

# home page
@app.route("/")
def main():
    return json.dumps(['message', 'Welcome to ORAS AI!'])

@app.route("/process/convert-pdf")
def convert_pdf():
    path = './data/1Amy.pdf'
    result = convertPDFToText(path=path)
    return json.dumps(result)

@app.route("/process/convert-docx")
def convert_docx():
    path = './data/1Amy.docx'
    result = convertDocxToText(path=path)
    return json.dumps(result)

@app.route("/process/extract-pdf")
def extract_pdf():
    url = request.args.get('url')
    result = extractTextFromPDF(url)
    return json.dumps(result)

@app.route("/process/extract-docx")
def extract_docx():
    url = request.args.get('url')
    result = extractTextFromDocx(url)
    return json.dumps(result)

# process the raw job description: remove stop words, punctuation
@app.route("/process/jd")
def prc_jd():
    raw_jd = request.form['jd']
    result = processJD(raw_jd)
    return json.dumps({"prc_jd": result})

@app.route("/process/cvs", methods = ['POST'])
def prc_cvs():
    urls = request.get_json()
    list_cv_content = {}
    for apply in urls['urls']:
        for id in apply:
            list_cv_content[id] = extractTextFromPDF(apply[id])
    # print(list_cv_content)
    processResume(list_cv_content)
    return json.dumps({'message': 'success'})

# calculate the similarity between document
@app.route("/calc/similarity")
def calc():
    
    data = request.get_json()
    
    # process job descripton
    jd = data['job_desc']
    job_description = processJD(jd)
    
    # process list resume
    list_cv_content = {}
    for apply in data['list_cv']:
        for id in apply:
            list_cv_content[id] = extractTextFromPDF(apply[id])
    processResume(list_cv_content)
    
    result = calcSimilar(job_description, len(list_cv_content))
    
    return json.dumps(result)

if __name__ == '__main__':
    app.run()