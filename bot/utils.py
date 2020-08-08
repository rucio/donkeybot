# bot modules
import bot.config as config
# general python
import re
import requests
import json
import pickle
import string
from datetime import datetime 
import pytz
import warnings
# text processing
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
nltk.download("stopwords", quiet=True)
nltk.download("wordnet", quiet=True)
nltk.download("punkt", quiet=True)


# DataFrame/Series related helper functions
def print_df_column(dataframe, column, max_rows=None):
    """
    Print the Series data in the column of the dataframe
    we chose.
    If the column doesn't exist it prints the error message
    
    :param dataframe  : dataframe containing the column
    :param column     : column whose data we want to print
    :param max_rows   : the maximum number of (top) rows we want to print
    :type max_rows    : None (to print all the rows) or int
    """
    try:
        if max_rows is None:
            max_rows = len(dataframe)
        for i in range(len(dataframe.head(max_rows))):
            print(f'\nRow {i} in {column} of the dataframe')
            print('###########################################')
            print(dataframe[column].values[i])
    except:
        print("<!>ERROR: in print_df_body()")
    return


def turn_Series_into_string(series_obj):
  """ 
  Turn a pandas Series object (of strings)
  into one large string. Intended for text columns
  in pandas DataFrames

  :param series_obj    : a pandas Series object (usually text column)
  :returns long_string : string of the series_obj
  """ 
  try:
    long_string = ''
    for i in range(len(series_obj)):
      long_string += series_obj.values[i]
      long_string += '\n'
    return long_string
  except:
    print("<!>ERROR in turn_into_string()")
    return

# General helper functions
def save_dict(dict_name, dict_data):
    """
    Save a dictionary in the data folder
    :param dict_name  : dictionary name
    :param dict_data  : dictionary
    """
    with open(config.DATA_DIR+dict_name+'.pickle', 'wb') as f:
        pickle.dump(dict_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def convert_to_utc(date, date_format):
    """
    Converts date to UTC based on the format.
    eg. in GitHub dates requested through the api
    we find the following format
    ISO 8601 format: YYYY-MM-DDTHH:MM:SSZ

    :param date   : String of the date
    :param format : Format of the string
    :returns date : String in utc format
    """
    date = datetime.strptime(date, date_format)
    if date.tzinfo is not None:
        #timezone aware object
        date = date.replace(tzinfo=pytz.UTC)- date.utcoffset()
    else:
        # turn unaware of timezones datetime object to aware
        date = pytz.utc.localize(date)
    return date


def request(url, headers):
    """
    Return the response from the url with the information saved in 
    a python dictionary.
    
    :param url : the url upon which the request is made
    :out r_dict: json response in python dict format
    """
    r = requests.get(url, headers=headers)
    r_dict = json.loads(r.text)
    return r_dict


# Text Processing related helper functions

def pre_process_text(
    text,
    lower_text=False,
    fix_url=False,
    remove_url=False,
    decontract_words=False,
    remove_newline=False,
    remove_numbers=False,
    numbers_replacement=None,
    remove_punctuation=False,
    punctuation_replacement=None,
    tokenize_text=False,
    remove_stop_words=False,
    stem=False,
    lemmatize=False
    ):
    """ 
    Perform the pre processing steps on the text in the order shown :
    And depending on what was set to True :
          (1) lowercase -> 
          (2) fix urls -> 
          (3) remove urls ->
          (4) remove_newline ->
          (5) decontract phrases ->
          (6) remove punctuation -> 
          (7) remove numbers -> 
          (8) remove stopwords -> 
          (9) stem words-> 
          (10) lemmatize words ->
          (11) remove extra whitespaces ->
          (12) tokenize words 
    
    <!> Note  : (11) remove extra whitespaces is done by default.
    
    :param punctuation_replacement      : Used when remove_punctuation = True 
                                        and we want to replace punctuation 
                                        not just remove it. Usefull because then
                                        there is no need for word segmentation.
    :param numbers_replacement          : Same as above for when remove_numbers = True
    :type text                          : String
    :type punctuation_replacement       : char or string (default None)
    :type numbers_replacement           : char or string (default None)
    :type *rest of params*              : Boolean

    :returns (if tokenize=True) words   : list of all words in text after processing
    :returns (if tokenize=False) text   : text processed depending on parameters
    """
    # 1
    if lower_text:
        text = text.lower()
    # 2
    if fix_url:
        text = fix_urls(text)
    # 3
    if remove_url:
        text = remove_URL(text)
    # 4
    if remove_newline:
        text = text.replace('\n', ' ')
    # 5
    if decontract_words:
        text = decontract(text)
    # 6
    if remove_punctuation:
        text = remove_chars(text, string.punctuation, replace_with=punctuation_replacement)
    # 7       
    if remove_numbers:
        text = remove_chars(text, string.digits, replace_with=numbers_replacement)
    # 8 
    if remove_stop_words:
        # warnings.simplefilter('ignore')
        stop_words_english = set(stopwords.words('english'))
        # warnings.simplefilter('always')
        text = ' '.join(token for token in nltk.word_tokenize(text)
                        if token.lower() not in stop_words_english)
    # 9 
    if stem:
        stemmer = nltk.stem.porter.PorterStemmer()
        text = ' '.join(stemmer.stem(token) for token in
                        nltk.word_tokenize(text))
    # 10 
    if lemmatize:
        # warnings.simplefilter('ignore')
        lemmatizer = WordNetLemmatizer()
        text = ' '.join(lemmatizer.lemmatize(token) for token in
                        nltk.word_tokenize(text))
        # warnings.simplefilter('always')
    # 11
    text = re.sub(' +', ' ', text).strip(' ')
    # 12
    if tokenize_text:
        words = nltk.word_tokenize(text)
        return words
    elif not tokenize_text:
        return text


def remove_URL(text):
    """Removes URLs from the text"""
    return re.sub(config.URL_REGEX, '', text)


def remove_chars(text, chars, replace_with=None):
    """
    Removes chars from text or replaces them with the input.
    Also removes any extra whitespaces which might have been 
    introduced.

    : param text         : text upon which the processing is done
    : param chars        : chars to search for in text and remove
    : param replace_with : any chars found in text will be replaced 
                           with replace_with input
    : type chars         : string of chars eg. ',.'{}#!'
    : return text        : processed text with removed or replaced chars
    """
    if replace_with is not None:
        remove_char_map = dict((ord(char), ord(replace_with)) for char in chars)
    else:
        remove_char_map = dict((ord(char), None) for char in chars)
    text = text.translate(remove_char_map)
    # remove extra whitespace created from above processing
    text = re.sub(' +', ' ', text).strip(' ')
    return text


def fix_urls(text):
    """
    Removes any newline \\n characters form inside urls
    Needed since our our URL_REGEX will think of newline characters
    as part of the url.

    :returns text : text with 'fixed' urls
    """
    if config.URL_REGEX.search(text)is not None:
        for quote_match in config.URL_REGEX.finditer(text):
            text = text[:quote_match.start()] + text[quote_match.start():quote_match.end()].replace( '\n', '') + text[quote_match.end():]
    return text


def span_urls(text):
    """Given a text, generates (start, end) spans of URLs in the text."""
    if config.URL_REGEX.search(text)is not None:
        for quote_match in config.URL_REGEX.finditer(text):
            yield (quote_match.start(), quote_match.end())



def decontract(phrase):
    """
    Substitutes occurrences in the text like
      n't to not
      're to are
      'll to will
    eg.
        haven't -> have not
        must've -> must have

    :type phrase    : string
    :returns phrase : decontracted phrase
    """
    # specific
    phrase = re.sub(r"won't", "will not", phrase)
    phrase = re.sub(r"can\'t", "can not", phrase)
    # general
    phrase = re.sub(r"n\'t", " not", phrase)
    phrase = re.sub(r"\'re", " are", phrase)
    phrase = re.sub(r"\'s", " is", phrase)
    phrase = re.sub(r"\'d", " would", phrase)
    phrase = re.sub(r"\'ll", " will", phrase)
    phrase = re.sub(r"\'t", " not", phrase)
    phrase = re.sub(r"\'ve", " have", phrase)
    phrase = re.sub(r"\'m", " am", phrase)
    return phrase



############################################################## 
# used in searchers/change later upon further analysis
def preprocess(text):
    """
    Remove puntuation, lower and tokenize text
    """
    return tokenize_this(remove_punctuation(text.lower()))
    
def remove_punctuation(text):
    """
    Remove all special character from text string
    """
    return text.translate(str.maketrans("", "", string.punctuation))

def tokenize_this(text):
    """
    Tokenize with NLTK
    Rules:
        - drop all words of 1 and 2 characters
        - drop all stopwords
        - drop all numbers
    """
    
    # warnings.simplefilter('ignore')
    stop_words_english = set(stopwords.words('english'))
    # warnings.simplefilter('always')
    words = nltk.word_tokenize(text)
    return list(
            set(
                [
                word
                for word in words
                if len(word) > 1
                    and not word in stop_words_english
                    and not word.isnumeric()
                ]
            )
        )


