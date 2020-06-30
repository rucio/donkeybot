

Turns out that Stanford NER and POS from nltk.tag are deprecated after v3.3 of nltk so we should follow what 
[Stanford-CoreNLP-API-in-NLTK docs](https://github.com/nltk/nltk/wiki/Stanford-CoreNLP-API-in-NLTK) say.


In this folder you will find the NER tagger implemented with  the depracated methods and the recommended CoreNLP API server. 
**I suggest we use the Core nlp API server.**


To run **NER-Stanford-with-CORE-NLP .py** on your machine you need to:
1) pip install requests
2) make sure you have java v1.8+
3) download : http://nlp.stanford.edu/software/stanford-corenlp-latest.zip
4) open the server by running the following command on the directory where the zip is saved
 ``` bash 
 java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer \
-preload tokenize,ssplit,pos,lemma,ner,parse,depparse \
-status_port 9000 -port 9000 -timeout 15000 
```


To run **NER-Stanford-depracated .py** on your machine you need to:
1) make sure you have java v1.8+
2) download : https://nlp.stanford.edu/software/stanford-ner-2018-10-16.zip
3) make sure that the absolute paths referenced inside the code are the   directories where you have java and the zip file installed.  
Mine for reference:  
``` python
os.environ["CLASSPATH"] = "D:\Other\stanford\stanford-ner-2018-10-16"
os.environ["STANFORD_MODELS"] = "D:\Other\stanford\stanford-ner-2018-10-16\classifiers"
os.environ['JAVAHOME'] = "C:\Program Files\Java\jdk1.8.0_241"  

stanford_dir = 'D:\Other\stanford\stanford-ner-2018-10-16'
jarfile = stanford_dir + '\stanford-ner.jar'
modelfile = stanford_dir + '\classifiers\english.all.3class.distsim.crf.ser.gz'
```  
  
