# bot modules
from bot.database.sqlite import Database
from bot.parser.comments import IssueComment, IssueCommentParser
import bot.config as config

# general python
from datetime import datetime
import os
import pytest


@pytest.fixture(scope="module")
def test_db():
    db = Database("test.db", "test_table")
    db.create_issue_comments_table("test_table")
    yield db
    db.close_connection()
    os.remove(config.DATA_DIR + "test.db")


@pytest.fixture(scope="module")
def test_comment(test_db):
    comment = dict()
    comment["issue_id"] = "3945"
    comment["comment_id"] = "677190524"
    comment["creator"] = "mlassnig"
    comment["created_at"] = "2020-08-20T05:47:15Z"
    comment["body"] = "Thanks for the report! Fortunately this is an easy fix!"
    comment["db"] = test_db
    comment["issue_comments_table"] = "test_table"
    yield comment


@pytest.fixture(scope="module")
def comment_parser(test_comment):
    parser = IssueCommentParser()
    yield parser


@pytest.fixture(scope="module")
def parsed_comment(test_comment, comment_parser):
    parsed_comment = comment_parser.parse(**test_comment)
    yield parsed_comment


@pytest.fixture(scope="module")
# parsed_comment because when we parse -> thats when its inserted into db
def test_comment_in_db(parsed_comment, test_db):
    the_comment_in_the_db = test_db.query(
        "SELECT * \
         FROM test_table\
         WHERE comment_id == 677190524"
    )[0]
    yield the_comment_in_the_db


def test_comment_data_saved_on_db(parsed_comment, test_comment_in_db):
    # columns fromon .create_issue_comments_table()
    assert test_comment_in_db[0] == parsed_comment.comment_id  # comment_id
    assert test_comment_in_db[1] == parsed_comment.issue_id  # issue_id
    assert test_comment_in_db[2] == parsed_comment.creator  # creator
    # date must have a specific format and parsed_comment.date is datetime obj
    assert test_comment_in_db[3] == parsed_comment.created_at.strftime(
        "%Y-%m-%d %H:%M:%S+00:00"
    )  # created_at
    assert test_comment_in_db[4] == parsed_comment.body  # body
    assert test_comment_in_db[5] == parsed_comment.clean_body  # clean_body


# should this be under sqlite test?
def test_comment_types_on_db(test_comment_in_db):
    assert type(test_comment_in_db[0]) == int  # comment_id
    assert type(test_comment_in_db[1]) == int  # issue_id
    assert type(test_comment_in_db[2]) == str  # creator
    assert type(test_comment_in_db[3]) == str  # created_at
    assert type(test_comment_in_db[4]) == str  # body
    assert type(test_comment_in_db[5]) == str  # clean_body


def test_parsed_comment_cls_type(parsed_comment):
    assert type(parsed_comment) == IssueComment


def test_parsed_comment_attribute_types(parsed_comment):
    assert type(parsed_comment.__dict__) == dict
    assert type(parsed_comment.comment_id) == int
    assert type(parsed_comment.issue_id) == int
    assert type(parsed_comment.creator) == str
    assert type(parsed_comment.created_at) == datetime
    assert type(parsed_comment.body) == str
    assert type(parsed_comment.clean_body) == str
