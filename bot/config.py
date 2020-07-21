import os.path
from pathlib import Path
import pickle
import re
import nltk
from nltk.corpus import stopwords


# stopwords
ENGLISH_STOPWORDS = list(set(stopwords.words("english")))
# we could get better results if we remove and append custom stopwords
# for example the word 'down' is considered a stopwords but what if a user asks
# why is this site down? Then we'll only have 'site', not ['site','down']
# so I should work on that
# CUSTOM_STOPWORDS = ...


# for absolute paths 
BOT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = BOT_DIR + '\..\data\\'
INPUT_DATA_DIR = BOT_DIR + '\..\data\inputs\\'
OUTPUT_DATA_DIR = BOT_DIR + '\..\data\outputs\\'

# for EmailParser
try:  
    with open(DATA_DIR+'conversation_dict.pickle', 'rb') as f:
        CONVERSATION_DICT = pickle.load(f)
except:
        CONVERSATION_DICT = {}

# removed for conversation creation when searching same subjects
REGEX_METACHARACTERS = '^$.|?*+(){}[]'

# reply emails quoting past emails
ON_HDR_REGEX = re.compile(r'On (.*?)wrote: ', re.IGNORECASE)
QUOTED_REGEX = re.compile(r'(>>+|> >+)')
HEADER_REGEX = re.compile(r'(([_-]{7,})?(\s)From:(.*)(Sent:)?(.*)To:(.*)Subject:)', re.IGNORECASE)
ORIGINAL_MSG_REGEX = re.compile(r'-----Original Message-----', re.IGNORECASE)

# url
URL_REGEX = re.compile(r'(https|http|www)[^ ]*')

# emails sent automatically : find what other patterns exist in those
# AUTOMATIC_MSG = re.compile(r'\\-- THIS IS AN AUTOMATICALLY GENERATED MESSAGE')

