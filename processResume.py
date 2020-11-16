import spacy
from spacy.vectors import Vectors
import pandas as pd
nlp = spacy.load('en_core_web_md')
vectors = Vectors(shape=(1000,300))
nlp.vocab.vectors = vectors
import re
re_c = re.compile(r'\w+')

def processResume(cv_content):
    
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

    # utility function to skip line when no alphabet present
    def is_empty(line):
        for c in line:
            if (c.isalpha()):
                return False
        return True

    dict_of_data_series = {}

    # main_content = ["CARRIE Professional Experience Citco Fund Services (Singapore) Pte Ltd", "May 2016", "Present", "Fund Accountant (Full-Time)", "Prepared 3 daily, 1 weekly and 14 monthly Fund-Level Net Asset Value computations and Financial Statements for over 15 Hedge Funds across 3 Databases using in-house software to be disseminated to shareholders worldwide", "Completed 35 Trader-Level Financial Statements and Net Asset Value calculations under 2 funds according to their individual Investment Advisory Agreements which accounted for 20% of the team's workload", "Liaised with over 10 Investment Managers and 10 Investor Relations Teams to bring about an increase in client's satisfaction by 20%", "Corresponded closely with 3 Pricing, Corporate Actions, Dividend and Reconciliations Teams respectively to improved delivery time of Financial Statements by 15%.", "Cross-trained 7 colleagues in a team of 9 to ensure that 12 funds in 2 databases were completed accurately based on individual clients request which developed bench strength by 20%", "Streamlined the process of migration of funds from other offices (such as Toronto, Dublin) to Singapore which increased migration efficiency by 20%", "Written 2 Standard Operating Procedures for the generation of Financial Statements and reviewed 1 Financial Statement.", "Completed 4 FIN 48 reports and assisted in answering more than 20 audit queries which reduced audit time taken by 25% Parsons Brinckerhoff Pte Ltd", "Aug 2013", "Feb 2016 IT Assistant (Full-Time)", "Provide Mentorship to 3 juniors thus increasing their technical abilities by 30%", "Leading a team of 3 to replaced 8 copiers over 4 levels of the company within a tight deadline of 3 days", "Working closely in a team of 7 with 3 senior colleagues in re-vamping of network structure within the given time constraint of 10hr", "Planning and executing of Data Migration 2 different office, ensuring over 1 TB of data are replicated at 99%", "Maintaining a IT Knowledge Base with over 50 created knowledge articles on SharePoint thus reducing troubleshooting time by 30% and decreased internal user downtime by 15%", "JK Technology Pte Ltd(Outsource to AIA Singapore)", "Oct 2011", "June 2013 Desktop Technician (Full-Time)", "workstations to increase work flow efficiency by 20%", "Providing excellent Customer service to over 500 users which increase Customer Satisfaction by 35%", "Devising a procedure in upgrading of Windows 7 over 500 computers which reduced down time by 25%", "Education Murdoch University", "May 2014", "Mar 2016 Kaplan Singapore", "Bachelor of Commerce in Accounting and Finance Singapore Polytechnic", "Apr 2006", "Apr 2009", "Diploma in Information Technology", "Other Certificates and Courses Attended CFA Institute", "Oct 2016", "CFA Institute Investment Foundations INTELLISOFT SYSTEMS", "Mar 2016", "Advanced MS Excel 2013", "Others Languages Spoken: English, Mandarin", "Language Written: English Computer Proficiency: Microsoft Excel, Word and Powerpoint Bloomberg Terminal Proficiency: Beginner", ""]

    previous_section  = 'extra'

    curr_data_series = pd.Series([""]*len(list_of_sections), index=list_of_sections)

    for line in cv_content:
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

        curr_line = ' '.join(list_of_imp_words_in_line)
        doc = nlp(curr_line)
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

        curr_data_series[previous_section] += mod_line

    dict_of_data_series['cv'] = curr_data_series
    # if flag_print:
    #     print(curr_data_series)

    data_frame = pd.DataFrame(dict_of_data_series)
    data_frame.to_csv('./data/prc_cv.csv', sep='\t')