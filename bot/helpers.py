# bot modules
import bot.config as config
# general python
import re
import pickle
import string
import nltk



def save_dict(dict_name, dict_data):
    """
    Save a dictionary in the data folder
    :param dict_name  : dictionary name
    :param dict_data  : dictionary
    """
    with open(config.DATA_DIR+dict_name+'.pickle', 'wb') as f:
        pickle.dump(dict_data, f, protocol=pickle.HIGHEST_PROTOCOL)


def remove_chars(text, chars):
    """
    Removes and specific chars  and extra whitespaces
    : type chars  : string of chars eg. ',.'{}#!'
    : return text : processed text
    """
    remove_punctuation_map = dict((ord(char), None) for char in chars)
    text = text.translate(remove_punctuation_map)
    # remove extra whitespace
    text = re.sub(' +', ' ', text).strip(' ')
    return text


def fix_urls(text):
    """Removes any newline \\n characters form inside urls"""
    if config.URL_REGEX.search(text)is not None:
        for quote_match in config.URL_REGEX.finditer(text):
            text = text[:quote_match.start()] + text[quote_match.start():quote_match.end()].replace( '\n', '') + text[quote_match.end():]
    return text


def span_urls(text):
    """Given a text, generates (start, end) spans of URLs in the text."""
    if config.URL_REGEX.search(text)is not None:
        for quote_match in config.URL_REGEX.finditer(text):
            yield (quote_match.start(), quote_match.end())







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
    words = nltk.word_tokenize(text)
    return list(
            set(
                [
                word
                for word in words
                if len(word) > 1
                    and not word in config.ENGLISH_STOPWORDS
                    and not word.isnumeric()
                ]
            )
        )