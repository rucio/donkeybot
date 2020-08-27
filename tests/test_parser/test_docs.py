# bot modules
from bot.database.sqlite import Database
from bot.parser.docs import RucioDocsParser, RucioDoc
import bot.config as config

# general python
import pandas as pd
import os
import pytest


@pytest.fixture(scope="module")
def test_db():
    print("\nsetting up")
    # db
    db = Database("test.db", "test_doc_table")
    db.create_docs_table("test_doc_table")
    yield db
    print("\nclosing up")
    db.close_connection()
    os.remove(config.DATA_DIR + "test.db")


@pytest.fixture(scope="module")
def test_doc(test_db):
    doc = dict()
    doc["doc_id"] = 999
    doc["name"] = "test_doc.md"
    doc["url"] = "https://rucio.readthedocs.io/en/latest/"
    # body larger than len(50) in test_doc
    doc["body"] = "".join(list(str(i) for i in range(51)))
    doc["doc_type"] = "test"
    doc["db"] = test_db
    doc["docs_table_name"] = "test_doc_table"
    yield doc


@pytest.fixture(scope="module")
def rucio_doc_parser(test_doc):
    parser = RucioDocsParser()
    yield parser


@pytest.fixture(scope="module")
def parsed_doc(test_doc, rucio_doc_parser):
    print(test_doc)
    parsed_doc = rucio_doc_parser.parse(**test_doc)
    yield parsed_doc


@pytest.fixture(scope="module")
# parsed_doc because when we parse -> thats when its inserted into db
def test_doc_in_db(parsed_doc, test_db):
    the_doc_in_the_db = test_db.query(
        "SELECT * \
         FROM test_doc_table\
         WHERE doc_id == 999"
    )[0]
    yield the_doc_in_the_db


def test_doc_data_saved_on_db(test_doc, test_doc_in_db):
    assert len(test_doc["body"]) >= 50
    # columns fromon .create_docs_table()
    assert test_doc_in_db[0] == test_doc["doc_id"]  # doc_id
    assert test_doc_in_db[1] == test_doc["name"]  # name
    assert test_doc_in_db[2] == test_doc["url"]  # url
    assert test_doc_in_db[3] == test_doc["body"]  # body
    assert test_doc_in_db[4] == test_doc["doc_type"]  # doc_type


def test_doc_types_on_db(test_doc, test_doc_in_db):
    assert len(test_doc["body"]) >= 50
    assert type(test_doc_in_db[0]) == int  # doc_id
    assert type(test_doc_in_db[1]) == str  # name
    assert type(test_doc_in_db[2]) == str  # url
    assert type(test_doc_in_db[3]) == str  # body
    assert type(test_doc_in_db[4]) == str  # doc_type


def test_that_db_empty_for_doc_with_len_lt_50(test_doc, rucio_doc_parser, test_db):
    small_body_doc = {k:v for k,v in test_doc.items()}
    small_body_doc["doc_id"] = 1000
    small_body_doc["body"] = "less than 50 chars"
    # small_body_doc["db"] = test_db
    small_body_parsed_doc = rucio_doc_parser.parse(**small_body_doc)
    small_body_doc_in_db = test_db.query(
        "SELECT * \
        FROM test_doc_table\
        WHERE doc_id == 1000"
    )
    assert len(small_body_doc["body"]) < 50
    # when len < 50 it should not be added to db
    assert small_body_doc_in_db == []


def test_parsed_doc_cls_type(parsed_doc):
    assert type(parsed_doc) == RucioDoc 


def test_parsed_doc_attribute_types(parsed_doc):
    assert type(parsed_doc.__dict__) == dict
    assert type(parsed_doc.doc_id) == int
    assert type(parsed_doc.name) == str
    assert type(parsed_doc.url) == str
    assert type(parsed_doc.body) == str
    assert type(parsed_doc.doc_type) == str


def test_parsed_doc_attribute_content(test_doc, parsed_doc):
    assert parsed_doc.doc_id == test_doc["doc_id"]
    assert parsed_doc.name == test_doc["name"]
    assert parsed_doc.url == test_doc["url"]
    assert parsed_doc.body == test_doc["body"]
    assert parsed_doc.doc_type == test_doc["doc_type"] 


def test_parser_text_processing(test_doc, rucio_doc_parser):
    extra_spaces_doc = {k:v for k,v in test_doc.items()}
    extra_spaces_doc["body"] += '     a     ' # 5 spaces + a + 5 spaces == 11 chars
    extra_spaces_doc["doc_id"] += 111 # must be unique id
    parsed_extra_spaces_doc = rucio_doc_parser.parse(**extra_spaces_doc)
    assert parsed_extra_spaces_doc.body == extra_spaces_doc["body"][:-11] + ' a'
