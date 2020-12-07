import math
from flask.helpers import total_seconds
import pandas as pd
from gensim.models import Word2Vec as w2v

# load model to process
model = w2v.load('./model/stackexchange_model_v2')

def calcSimilar(job_description, no_of_cv):
    
    print('>> Calculate similarity')

    cvs = pd.read_csv('./data/prc_cvs.csv', sep='\t')
    cvs = cvs.set_index('Unnamed: 0')
    
    word_value = {}
    similar_words_needed = 5
    total_word_value = 0
    jd_value = 0
    for word in job_description.split():
        # get similar word
        similar_words, similarity = get_closest(word, similar_words_needed)
        for i in range(len(similar_words)):
            word_value[similar_words[i]] = word_value.get(similar_words[i], 0)+similarity[i]
            total_word_value += word_value[similar_words[i]]
            # print(similar_words[i], word_value[similar_words[i]])
    
    print(">> ", total_word_value)
    print(">> ", len(job_description.split()))
    # no_of_cv = 1

    count = {}
    idf = {}
    for word in word_value.keys():
        count[word] = 0
        for i in range(no_of_cv):
            try:
                if word in str(cvs.loc(0)['edu'][i]).split() or word in str(cvs.loc(0)['skill'][i]).split() or word in str(cvs.loc(0)['exp'][i]).split() or word in str(cvs.loc(0)['extra'][i]).split():
                    count[word] += 1
            except Exception as e:
                print('>> error at cv ', i)
                print(e)
                pass
        if (count[word] == 0):
            count[word] = 1
        idf[word] = math.log(no_of_cv/count[word])
        jd_value += word_value[word]*idf[word]
    #
    print('>> jd_value: ', jd_value)
    
    score = {}
    for i in range(no_of_cv):
        score[i] = 0
        tmp_score = 0
        try:
            for word in word_value.keys():
                tf = str(cvs.loc(0)['edu'][i]).split().count(word) + str(cvs.loc(0)['skill'][i]).split().count(word) + str(cvs.loc(0)['exp'][i]).split().count(word) + str(cvs.loc(0)['extra'][i]).split().count(word)
                tmp_score += word_value[word]*tf*idf[word]
            #
            print('>> score of cv ', i, ': ', tmp_score)

            # convert score to percentage
            tmp = tmp_score/(jd_value/(similar_words_needed + 1))*100
            if (tmp > 100):
                score[i] = 100
            else:
                score[i] = tmp
        except Exception as e:
            print('>> error at cv ', i)
            print(e)
            pass
    
    sorted_list = []
    for i in range(no_of_cv):
        # sorted_list.append((round(score[i]), i))
        sorted_list.append((round(score[i]), i))
        
    sorted_list.sort(reverse=True)

    result = {}
    for s, i in sorted_list:
        if list(cvs)[i] != '.DS_Store':
            result[list(cvs)[i]] = s
    
    return result

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