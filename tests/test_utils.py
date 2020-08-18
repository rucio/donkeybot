# bot modules
import bot.utils as utils
import bot.config as config

# general python
import pytest
import pickle
import os

data_dir = dict_name = dict_data = None
test_file = None


def setup_module(module):
    global dict_name, dict_data, data_dir
    dict_name = "test_dict"
    dict_data = {"this": "is a test"}
    data_dir = config.DATA_DIR
    utils.save_dict(dict_name=dict_name, dict_data=dict_data)


def teardown_module(module):
    os.remove(data_dir + dict_name + ".pickle")


def test_save_dict_existence():
    global test_file
    try:
        with open(data_dir + dict_name + ".pickle", "rb") as f:
            test_file = pickle.load(f)
    except Exception as _e:
        pytest.fail(_e)


def test_save_dict_contents():
    assert test_file == dict_data


def test_save_dict_type():
    assert type(test_file) == dict


def test_convert_to_utc_for_email_dates():
    email_date_format = "%a, %d %b %Y %H:%M:%S %z"
    date_1 = "Wed, 27 Mar 2019 13:02:11 +0100"
    expected_utc_date_1 = "2019-03-27 12:02:11+00:00"
    date_2 = "Tue, 15 Jan 2019 10:24:40 -0500"
    expected_utc_date_2 = "2019-01-15 15:24:40+00:00"
    assert str(utils.convert_to_utc(date_1, email_date_format)) == expected_utc_date_1
    assert str(utils.convert_to_utc(date_2, email_date_format)) == expected_utc_date_2


def test_convert_to_utc_for_github_dates():
    # GitHub API uses ISO 8601 format: "%Y-%m-%dT%H:%M:%SZ"
    github_date_format = "%Y-%m-%dT%H:%M:%SZ"
    date_1 = "2020-08-14T09:07:27Z"
    expected_utc_date_1 = "2020-08-14 09:07:27+00:00"
    date_2 = "2018-01-25T12:08:49Z"
    expected_utc_date_2 = "2018-01-25 12:08:49+00:00"
    assert str(utils.convert_to_utc(date_1, github_date_format)) == expected_utc_date_1
    assert str(utils.convert_to_utc(date_2, github_date_format)) == expected_utc_date_2


def test_pre_process_text_extra_whitespace():
    text = "   text    wont    contain    extra    spaces   "
    correct_text = "text wont contain extra spaces"
    assert utils.pre_process_text(text) == correct_text


def test_lower_with_pre_process_text():
    text = "A SAMPLE TEXT with upper case"
    assert utils.pre_process_text(text, lower_text=True) == text.lower()


def test_fix_urls():
    text = (
        "text with url : https://g\nithub.com/ru\ncio/rucio that has line newline char"
    )
    correct_text = (
        "text with url : https://github.com/rucio/rucio that has line newline char"
    )
    assert utils.fix_urls(text) == correct_text


def test_fix_urls_with_pre_process_text():
    text = (
        "text with url : https://g\nithub.com/ru\ncio/rucio that has line newline char"
    )
    correct_text = (
        "text with url : https://github.com/rucio/rucio that has line newline char"
    )
    assert utils.pre_process_text(text, fix_url=True) == correct_text


def test_span_urls():
    text = "text with url : https://g\nithub.com/ru\ncio/rucio"
    correct_span = [(16, 48)]  # each \n counts as 1
    spans_1 = list(utils.span_urls(text))
    start_1, end_1 = spans_1[0][0], spans_1[0][1]

    text_2 = "text with url : https://github.com/rucio/rucio"
    correct_span_2 = [(16, 46)]
    spans_2 = list(utils.span_urls(text_2))
    start_2, end_2 = spans_2[0][0], spans_2[0][1]

    assert spans_1 == correct_span
    assert text[start_1:end_1] == "https://g\nithub.com/ru\ncio/rucio"
    assert spans_2 == correct_span_2
    assert text_2[start_2:end_2] == "https://github.com/rucio/rucio"


def test_remove_url():
    text = "text with url : https://g\nithub.com/ru\ncio/rucio"
    text_2 = "text with url : https://github.com/rucio/rucio"
    correct_text = "text with url : "
    assert utils.remove_URL(text) == correct_text
    assert utils.remove_URL(text_2) == correct_text


def test_remove_url_with_pre_process_text():
    # pre_process_text removes trailing/extra whitespaces
    # thus the correct_text doesn't have one
    text = "text with url : https://g\nithub.com/ru\ncio/rucio"
    text_2 = "text with url : https://github.com/rucio/rucio"
    correct_text = "text with url :"
    assert utils.pre_process_text(text, remove_url=True) == correct_text
    assert utils.pre_process_text(text, remove_url=True) == correct_text


def test_remove_newline_with_pre_process_text():
    # is not supposed to concat words that are broken from newline char
    text = "text\n with multi\nple newline\n chars"
    correct_text = "text with multi ple newline chars"
    assert utils.pre_process_text(text, remove_newline=True) == correct_text


def test_decontract():
    text = "won't, can't, shouldn't, we're, that's, I'd, we'll, aren't, they've, I'm"
    correct_text = "will not, can not, should not, we are, that is, I would, we will, are not, they have, I am"
    assert utils.decontract(text) == correct_text


def test_decontract_with_pre_process_text():
    text = "won't, can't, shouldn't, we're, that's, I'd, we'll, aren't, they've, I'm"
    correct_text = "will not, can not, should not, we are, that is, I would, we will, are not, they have, I am"
    assert utils.pre_process_text(text, decontract_words=True) == correct_text


def test_remove_punctuation_with_pre_process_text():
    # remember, pre_process_text removes extra whitespaces
    text = """Here is all the punctuation : !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""
    correct_text = """Here is all the punctuation"""
    assert utils.pre_process_text(text, remove_punctuation=True) == correct_text


def test_replace_punctuation_with_pre_process_text():
    text = """Here is all the punctuation : !"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"""
    correct_text = "Here is all the punctuation h hhhhhhhhhhhhhhhhhhhhhhhhhhhhhhhh"
    assert (
        utils.pre_process_text(
            text, remove_punctuation=True, punctuation_replacement="h"
        )
        == correct_text
    )


def test_remove_numbers_with_pre_process_text():
    text = "Here are all the numbers : 1234567890 ;)"
    correct_text = "Here are all the numbers : ;)"
    assert utils.pre_process_text(text, remove_numbers=True) == correct_text


def test_replace_numbers_with_pre_process_text():
    text = "Here are all the numbers : 1234567890 ;)"
    correct_text = "Here are all the numbers : hhhhhhhhhh ;)"
    assert (
        utils.pre_process_text(text, remove_numbers=True, numbers_replacement="h")
        == correct_text
    )


def test_remove_chars():
    text = "This text instead of the characters 'e' and 'i' will have 'z'"
    correct_text = "Thzs tzxt znstzad of thz charactzrs 'z' and 'z' wzll havz 'z'"
    assert utils.remove_chars(text, "ei", replace_with="z") == correct_text


def test_remove_chars_extra_whitespace():
    text = "   text    wont    contain    extra    spaces   "
    correct_text = "text wont contain extra spaces"
    assert utils.remove_chars(text, "", replace_with="") == correct_text


def test_remove_stopwords_with_pre_process_text():
    # nltk's word tokenizer might break tokens a bit weird eg. "->" to "- >"
    text = "random stopwords -> our she when or too from how am re most while will"
    correct_text = "random stopwords - >"
    assert utils.pre_process_text(text, remove_stop_words=True) == correct_text


def test_stemmer_with_pre_process_text():
    # nltk's word tokenizer might break tokens a bit weird eg. "->" to "- >"
    words = ["program", "programs", "programer", "programing", "programers"]
    root = "program"
    for word in words:
        assert utils.pre_process_text(word, stem=True) == root


def test_lemmatizer_with_pre_process_text():
    # nltk's word tokenizer might break tokens a bit weird eg. "->" to "- >"
    test_words = {"rocks": "rock", "corpora": "corpus", "developers": "developer"}
    for word in test_words.keys():
        assert utils.pre_process_text(word, lemmatize=True) == test_words[word]


def test_custom_request():
    headers = {"Content-Type": "application/json"}
    test_issue = "https://api.github.com/repos/rucio/rucio/issues/5"
    response = utils.request(test_issue, headers)
    assert response["number"] == 5
    assert response["title"] == "This is a test issue"
    assert response["body"] == "test!"
    assert response["created_at"] == "2017-11-07T13:03:03Z"
    assert response["assignees"][0]["login"] == "bari12"
    assert type(response) == dict
