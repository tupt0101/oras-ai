import json, datetime
import spacy
from spacy.vectors import Vectors
import pandas as pd
nlp = spacy.load('en_core_web_md')
vectors = Vectors(shape=(1000,300))
nlp.vocab.vectors = vectors
import re
re_c = re.compile(r'\w+')

def processJD(raw_jd):
    
    # clean text
    list_of_words = re_c.findall(raw_jd)
    list_of_imp_words  = []
    
    # remove stop word
    for i in range(len(list_of_words)):
        modified_word = modify(list_of_words[i])
        if (modified_word):
            list_of_imp_words.append(modified_word)

    modified_doc = ' '.join(list_of_imp_words)
    doc = nlp(modified_doc)
    
    result = ''
    # lemma string
    for token in doc:
        result += token.lemma_ + ' '
    print('>> processed jd: ', result)
    
    return result

def processResume(list_cv_content):
    
    print('>> Process resumes')
    # define flag variable
    flag_print = True
    threshold = 0.5

    # to get extract sections from the resume -- add or remove from  'similar_to' accordingly
    similar_to = {
        'edu' : ['education', 'study', 'academics', 'institute', 'school', 'college', 'qualifications', 'courses', 'certificates'],
        'exp' : ['job', 'internship', 'training', 'research', 'career', 'profession', 'role', 'project', 'responsibility', 'description', 'work experience', 'workshop', 'conference', 'experience'],
        'skill' : ['skill', 'languages', 'framework', 'tools'],
        'extra' : ['introduction', 'intro', 'achievement', 'hobby', 'links', 'additional', 'personal', 'award', 'objective', 'miscellaneous', 'interest', 'references']
    }

    list_of_sections = similar_to.keys()

    # to bring similar_words to their normal forms
    for section in list_of_sections:
        new_list = []
        
        for word in similar_to[section]:
            docx = nlp(word)
            new_list.append(docx[0].lemma_)
            
        # if flag_print:
        #     print(section, new_list)
            
        similar_to[section] = new_list

    # utility function to skip line when no alphabet present
    def is_empty(line):
        for c in line:
            if (c.isalpha()):
                return False
        return True

    dict_of_data_series = {}
    
    for id in list_cv_content.keys():

        previous_section  = 'extra'

        current_data_series = pd.Series([""]*len(list_of_sections), index=list_of_sections)

        for line in list_cv_content.get(id):
            # skip line if empty
            if (len(line.strip()) == 0 or is_empty(line)):
                continue
            
            # processing next line
            list_of_words_in_line = re_c.findall(line)
            list_of_imp_words_in_line  = []
            
            for i in range(len(list_of_words_in_line)):
                modified_word = modify(list_of_words_in_line[i])

                if (modified_word):
                    list_of_imp_words_in_line.append(modified_word)

            current_line = ' '.join(list_of_imp_words_in_line)
            doc = nlp(current_line)
            section_value = {}
            
            # initializing section values to zero
            for section in list_of_sections:
                section_value[section] = 0.0
            section_value[None] = 0.0
            
            # updating section values    
            for token in doc:
                for section in list_of_sections:
                    for word in similar_to[section]:
                        word_token = doc.vocab[word]
                        section_value[section] = max(section_value[section], float(word_token.similarity(token)))    
                        # print(token, section, word, section_value[section])
            
            # determining the next section based on section values and threshold
            most_likely_section = None
            for section in list_of_sections:
                # print('>>', section, section_value[section])
                if (section_value[most_likely_section] < section_value[section] and section_value[section] > threshold):
                    most_likely_section = section
            
            # updating the section
            if (previous_section != most_likely_section and most_likely_section is not None):
                previous_section = most_likely_section
                
            # writing data to the pandas series
            try:
                docx = nlp(line)
            except:
                continue  # to handle the odd case of characters like 'x02', etc.
            mod_line = ''
            for token in docx:
                if (not token.is_stop):
                    mod_line += token.lemma_ + ' '

            current_data_series[previous_section] += mod_line

        dict_of_data_series[id] = current_data_series
        # if flag_print:
        #     print(current_data_series)

    data_frame = pd.DataFrame(dict_of_data_series)
    data_frame.to_csv('./data/prc_cvs.csv', sep='\t')
    
    print(list_cv_content.keys() ,'end pc rsm: ', datetime.datetime.now())
    
# function to remove unnecessary symbols and stopwords 
def modify(word):
    try:
        symbols = '''~'`!@#$%^&*)(_+-=}{][|\:;",./<>?'''
        mod_word = ''
        
        for char in word:
            if (char not in symbols):
                mod_word += char.lower()

        docx = nlp(mod_word)

        if (len(mod_word) == 0 or docx[0].is_stop):
            return None
        else:
            return docx[0].lemma_
    except:
        return None # to handle the odd case of characters like 'x02', etc.