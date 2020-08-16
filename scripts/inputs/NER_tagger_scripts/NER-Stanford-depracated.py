"""
This script works, but the methods used are depracated after ntlk3.3
as per the docs https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK)

You will have to 
# Step 1 : download https://nlp.stanford.edu/software/stanford-ner-2018-10-16.zip
# Step 2 : make sure you have java v1.8+
# Step 3 : change the absolute paths below when we set the enviroment variables
           to what you have on your system
"""
import os
import hashlib
from copy import deepcopy
import nltk

# NER Tagger
from nltk.tag import StanfordNERTagger

os.environ["CLASSPATH"] = "D:\Other\stanford\stanford-ner-2018-10-16"
os.environ["STANFORD_MODELS"] = "D:\Other\stanford\stanford-ner-2018-10-16\classifiers"
os.environ["JAVAHOME"] = "C:\Program Files\Java\jdk1.8.0_241"

stanford_dir = "D:\Other\stanford\stanford-ner-2018-10-16"
jarfile = stanford_dir + "\stanford-ner.jar"
modelfile = stanford_dir + "\classifiers\english.all.3class.distsim.crf.ser.gz"

ner_tagger = StanfordNERTagger(modelfile, jarfile, encoding="utf-8")


def get_continuous_chunks(tagged_sent):
    continuous_chunk = []
    current_chunk = []

    for token, tag in tagged_sent:
        if current_chunk:  # if the current chunk is not empty
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
            if tag != "O":
                current_chunk.append((token, tag))
                prev_tag = tag

    return continuous_chunk


def _remove_names(text):
    """
    This function is more along the lines of what you already used
    chunks together named entities. 
    
    NER will tag John Doe as ('John', 'Person') and ('Doe', 'Person')
    if we want to chunk the above together and have only one hash
    ('John Doe', 'Person') we need to chunk same type named entities together
    
    This also chunkes together other named entities and might create problems
    in instances where the text is in the lines of "Joe, Mark and Robin ..."
    where our output will be ('Joe Mark Robin', 'PERSON')
    """
    if "CN=" in text:
        text.replace("CN=", "CN= ")
    person = []
    names = {}
    text_corrected = ""
    for sent in nltk.sent_tokenize(text):
        tagged_sent = ner_tagger.tag(sent.split())
        named_entities = get_continuous_chunks(tagged_sent)

        named_entities_str_tag = [
            (" ".join([token for token, tag in ne]), ne[0][1]) for ne in named_entities
        ]
        for tag in named_entities_str_tag:
            if tag[1] == "PERSON":
                person = tag[0]
                name_hash = hashlib.md5(str(person).encode("utf-8")).hexdigest()[:6]
                names[str(person)] = name_hash
                if " " in person:  # more than a single name
                    full_name = person.split()
                    first_name = full_name[0]
                    surname = full_name[1]
                    if len(full_name) > 2:
                        names[first_name + " " + surname] = name_hash
                    names[surname] = name_hash
                    names[surname.lower()] = name_hash

        text_corrected = deepcopy(text)
        for name, name_hash in names.items():
            text_corrected = text_corrected.replace(name, name_hash)
        return names, text_corrected


random_text = """House Speaker John Boehner became animated Tuesday over the proposed Keystone Pipeline, castigating the Obama administration for not having approved the project yet.
Republican House Speaker John Boehner says there's "nothing complex about the Keystone Pipeline," and that it's time to build it.
"Complex? You think the Keystone Pipeline is complex?!" Boehner responded to a questioner. "It's been under study for five years! We build pipelines in America every day. Do you realize there are 200,000 miles of pipelines in the United States?"
"""

names, text_corrected = _remove_names(random_text)

print(names, "\n\n")
print("RANDOM TEXT:")
print(text_corrected)
