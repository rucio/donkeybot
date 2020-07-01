# Name Tagger

In preparation of the input data we have to keep user's information private, this means that their names need to be hashed. There is a simple method to do this which is by using Named Entity Recognition to identify PERSON named entities and then hash them. But, this approach also leads to some mistakes, due to the layout of the emails and the multitude of nationalities and names of Rucio user's and CERN-HSF employees. Thus, some additional approaches besides the NER tagger were used to keep everyone's name private.

The Named Entity Recognition model that we used was [Stanford's NER tagger](https://nlp.stanford.edu/software/CRF-NER.html) and we utilized the [CoreNLPParser](https://www.nltk.org/_modules/nltk/parse/corenlp.html) class that the [Natural Language Toolkit](https://www.nltk.org/) (NLTK) provides. Once we run through all `(sender,receiver,body,subject)` columns of an email, we use the name tagger to identify PERSON named entities and then we substitute the names with their md5 hash using hashlib. 

A local copy of the `Name:Hash` pairs is kept on the Rucio team's side. Then the initial .db file is sent and used as input for phase 1 of the bot. For more information read our [Approach](approach.md).

You can actually try out the Named Entities Recognition model and many others that are provided with CoreNLP right on your browser by visiting : http://corenlp.run/ 

## Installation 
The Stanford NER and POS taggers from nltk.tag are deprecated as of nltk v3.3 which was our original approach so we should follow what 
[Stanford-CoreNLP-API-in-NLTK docs](https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK) says.

Basically, before deploying CoreNLP server on your machine you need to:
1) Make sure you have java v1.8+
2) Download : http://nlp.stanford.edu/software/stanford-corenlp-latest.zip

## Deployment
Open the server by running the following command on the directory where the zip is saved
 ``` bash 
$ java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
    -preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
    -status_port 9000 -port 9000 -timeout 15000 
```

You can go on `localhost:9000` or whichever port you chose and try out the model right there.
Or use python and nltk