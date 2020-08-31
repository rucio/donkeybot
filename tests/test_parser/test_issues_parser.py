# bot modules
from bot.database.sqlite import Database
from bot.parser.issues import IssueParser, Issue
import bot.config as config

# general python
from datetime import datetime
import os
import pytest


@pytest.fixture(scope="module")
def test_db():
    db = Database("test.db", "test_table")
    db.create_issues_table("test_table")
    yield db
    db.close_connection()
    os.remove(config.DATA_DIR + "test.db")


@pytest.fixture(scope="module")
def test_issue(test_db):
    issue = dict()
    issue["issue_id"] = "5"
    issue["title"] = "This is a test issue"
    issue["state"] = "closed"
    issue["creator"] = "rucio"
    issue["created_at"] = "2017-11-07T13:03:03Z"
    issue["comments"] = 1  # must have at least 1 comment to be inserted in db
    issue["body"] = "test!"
    issue["db"] = test_db
    issue["issues_table_name"] = "test_table"
    yield issue


@pytest.fixture(scope="module")
def issue_parser(test_issue):
    parser = IssueParser()
    yield parser


@pytest.fixture(scope="module")
def parsed_issue(test_issue, issue_parser):
    parsed_issue = issue_parser.parse(**test_issue)
    yield parsed_issue


@pytest.fixture(scope="module")
# parsed_issue because when we parse -> thats when its inserted into db
def test_issue_in_db(parsed_issue, test_db):
    the_issue_in_the_db = test_db.query(
        "SELECT * \
         FROM test_table\
         WHERE issue_id == 5"
    )[0]
    yield the_issue_in_the_db


def test_issue_data_saved_on_db(parsed_issue, test_issue_in_db):
    # columns fromon .create_issues_table()
    assert test_issue_in_db[0] == parsed_issue.issue_id  # issue_id
    assert test_issue_in_db[1] == parsed_issue.title  # title
    assert test_issue_in_db[2] == parsed_issue.state  # state
    assert test_issue_in_db[3] == parsed_issue.creator  # creator
    # date must have a specific format and parsed_issue.date is datetime obj
    assert test_issue_in_db[4] == parsed_issue.created_at.strftime(
        "%Y-%m-%d %H:%M:%S+00:00"
    )  # created_at
    assert test_issue_in_db[5] == parsed_issue.comments  # comments
    assert test_issue_in_db[6] == parsed_issue.body  # body
    assert test_issue_in_db[7] == parsed_issue.clean_body  # clean_body


# should this be under sqlite test?
def test_issue_types_on_db(test_issue_in_db):
    assert type(test_issue_in_db[0]) == int  # issue_id
    assert type(test_issue_in_db[1]) == str  # title
    assert type(test_issue_in_db[2]) == str  # state
    assert type(test_issue_in_db[3]) == str  # creator
    assert type(test_issue_in_db[4]) == str  # created_at
    assert type(test_issue_in_db[5]) == int  # comments
    assert type(test_issue_in_db[6]) == str  # body
    assert type(test_issue_in_db[7]) == str  # clean_body


def test_parsed_issue_cls_type(parsed_issue):
    assert type(parsed_issue) == Issue


def test_parsed_issue_attribute_types(parsed_issue):
    assert type(parsed_issue.__dict__) == dict
    assert type(parsed_issue.issue_id) == int
    assert type(parsed_issue.title) == str
    assert type(parsed_issue.state) == str
    assert type(parsed_issue.creator) == str
    assert type(parsed_issue.created_at) == datetime
    assert type(parsed_issue.comments) == int
    assert type(parsed_issue.body) == str
    assert type(parsed_issue.clean_body) == str


def test_clean_issue_body(issue_parser):
    body = """Motivation\r
              ----------
              This should 

              Modification\r
              ------------
              be visible
              
              Expected behavior\r
              ------------
              hi
            """
    clean_body = issue_parser.clean_issue_body(body)
    assert clean_body == "This should be visible hi"
