import math, json
import pandas as pd
import numpy as np

from flask import Flask, request

from gensim.models import Word2Vec as w2v

from convertDocxToText import convertDocxToText
from convertPDFToText import convertPDFToText
from extractFromPdfURL import extractTextFromPDF
from extractFromDocxURL import extractTextFromDocx
from processResume import processResume
from processJD import processJD

app = Flask(__name__)

# load model to process
model = w2v.load('./model/stackexchange_model_v2')

# home page
@app.route("/")
def main():
    return json.dumps(['message', 'Hello, world!'])

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

@app.route("/process/cv")
def prc_cv():
    cv_url = request.args.get('url')
    cv_content = extractTextFromPDF(cv_url)
    processResume(cv_content)
    return json.dumps({'message': 'success'})

# calculate the similarity between document
@app.route("/calc/similarity")
def calc():
    jd = request.form['jd']
    # cv_url = request.form['url']
    
    # extract cv content from url
    # cv_content = extractTextFromPDF(cv_url)
    
    # process job description and resume
    job_description = processJD(jd)
    # processResume(cv_content)
    
    cvs = pd.read_csv('./data/prc_cv.csv', sep='\t')
    cvs = cvs.set_index('Unnamed: 0')

    word_value = {}
    similar_words_needed = 2
    for word in job_description.split():
        # get similar word
        similar_words, similarity = get_closest(word, similar_words_needed)
        for i in range(len(similar_words)):
            word_value[similar_words[i]] = word_value.get(similar_words[i], 0)+similarity[i]
            # print(similar_words[i], word_value[similar_words[i]])
    
    # no_of_cv = 150
    no_of_cv = 1

    count = {}
    idf = {}
    for word in word_value.keys():
        count[word] = 0
        for i in range(no_of_cv):
            try:
                if word in cvs.loc(0)['skill'][i].split() or word in cvs.loc(0)['exp'][i].split():
                    count[word] += 1
            except:
                pass
        if (count[word] == 0):
            count[word] = 1
        idf[word] = math.log(no_of_cv/count[word])
    
    score = {}
    for i in range(no_of_cv):
        score[i] = 0
        try:
            for word in word_value.keys():
                tf = cvs.loc(0)['skill'][i].split().count(word) + cvs.loc(0)['exp'][i].split().count(word)
                score[i] += word_value[word]*tf*idf[word]
        except:
            pass
    
    sorted_list = []
    for i in range(no_of_cv):
        sorted_list.append((score[i], i))
        
    sorted_list.sort(reverse=True)

    # for s, i in sorted_list:
    #     if list(cvs)[i] != '.DS_Store':
    #         print(list(cvs)[i], ':', s)
    
    return json.dumps(sorted_list)

def get_closest(word, n):
    '''Get n most similar words by words'''
    # This function can easily expanded to get similar words to phrases--
    # using sent2vec() method defined in WithWord2Vec notebook
    word = word.lower()
    words = [word]
    similar_values = [1]
    try:
        similar_list = model.most_similar(positive=[word], topn=n)
        
        for tupl in similar_list:
            words.append(tupl[0])
            similar_values.append(tupl[1])
    except:
        # If word not in vocabulary return same word and 1 similarity--
        # see initialization of words, similarities.
        pass
    
    return words, similar_values

if __name__ == '__main__':
    app.run()