'''
To be able to run this script you need to have downloaded  '
the latest package of CoreNLP from http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
Then you need to follow guide in https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK
which will tell you how to open the API server on port 9000 
''' 


import os
import hashlib
from copy import deepcopy
import nltk
import requests


from nltk.parse import CoreNLPParser
# NER Tagger
ner_tagger = CoreNLPParser(url='http://localhost:9000', tagtype='ner')
# print(list(ner_tagger.tag(('Rami Eid is studying at Stony Brook University in NY'.split()))))


def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []

    for token, tag in tagged_sent:
        if current_chunk: # if the current chunk is not empty
            if tag != "O" and tag == prev_tag:
                current_chunk.append((token, tag))
                prev_tag = tag
            else:
                continuous_chunk.append(current_chunk)
                current_chunk = []
                current_chunk.append((token, tag))
                prev_tag = tag
        else:
            # every time the current chunk is empty we come here
            if tag!= "O":
                current_chunk.append((token, tag))
                prev_tag = tag
        
    # # Flush the final current_chunk into the continuous_chunk, if any.
    # if current_chunk:
    #     continuous_chunk.append(current_chunk)
    return continuous_chunk



def remove_names(text):
    '''
    This function is more along the lines of what you already used
    chunks together named entities. 
    
    NER will tag John Doe as ('John', 'Person') and ('Doe', 'Person')
    if we want to chunk the above together and have only one hash
    ('John Doe', 'Person') we need to chunk same type named entities together
    
    This also chunkes together other named entities and might create problems
    in instances where the text is in the lines of "Joe, Mark and Robin ..."
    where our output will be ('Joe Mark Robin', 'PERSON')
    '''
    if 'CN=' in text:
        text.replace('CN=', 'CN= ')
    person = []
    names = {}
    text_corrected = ""
    for sent in nltk.sent_tokenize(text):
        tagged_sent = ner_tagger.tag(sent.split())
        named_entities = get_continuous_chunks(tagged_sent)
        named_entities_str_tag = [(" ".join([token for token, tag in ne]), ne[0][1]) for ne in named_entities]
        for tag in named_entities_str_tag:
            if tag[1] == 'PERSON':
                person = tag[0]
                name_hash = hashlib.md5(str(person).encode('utf-8')).hexdigest()[:6]
                # names[str(person)] = name_hash
                if ' ' in person: # more than a single name
                    full_name = person.split()
                    first_name = full_name[0]
                    surname = full_name[1]
                    # if len(full_name) > 2:
                    #     names[first_name+' '+surname] = name_hash
                    names[surname] = name_hash
                    names[surname.lower()] = name_hash

    text_corrected = deepcopy(text)
    for name, name_hash in names.items():
        text_corrected = text_corrected.replace(name, name_hash)
        
    return names, text_corrected



random_text = '''House Speaker John Boehner became animated Tuesday over the proposed Keystone Pipeline, castigating the Obama administration for not having approved the project yet.
Republican House Speaker John Boehner says there's "nothing complex about the Keystone Pipeline," and that it's time to build it.
"Complex? You think the Keystone Pipeline is complex?!" Boehner responded to a questioner. "It's been under study for five years! We build pipelines in America every day. Do you realize there are 200,000 miles of pipelines in the United States?"
'''
random_text = "from Mario Lassnig <Mario.Lassnig@cern.ch>"


names, text_corrected = remove_names(random_text)

print(names, '\n\n')
print("RANDOM TEXT:")
print(text_corrected)
