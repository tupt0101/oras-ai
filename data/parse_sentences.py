import os
import spacy
nlp = spacy.load('en_core_web_sm')

import logging
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

path = '/home/tupt/Documents/QuoraScraperData/answers'

sent_file = open(os.path.join(path, "sentences.txt"), 'w')

with open(os.path.join(path, 'answers_.txt')) as fobj:
    for line in fobj:
        if line != '\n':
            try:
                doc = nlp(line)
            except:
                logging.warning(path, ":", line, " can't be parsed.")
                continue
            
            for each in doc.sents:
                sent_file.write(each.text + '\n')

sent_file.close()