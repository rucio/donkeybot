# bot modules
from bot.question.issues import IssueQuestion
from bot.database.sqlite import Database

# general python
import pytest


@pytest.fixture
def issue_question():
    question = IssueQuestion(
        question_text="Did the test pass?", start_idx=0, end_idx=18
    )
    return question


@pytest.fixture(scope="module")
def test_db():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


def test_attribute_error_when_set_origin_id_not_used(issue_question):
    with pytest.raises(AttributeError):
        issue_question.email_id
    with pytest.raises(AttributeError):
        issue_question.issue_id
    with pytest.raises(AttributeError):
        issue_question.comment_id


def test_origin_of_issue_question(issue_question):
    assert issue_question.origin == "issue"


def test_set_origin_id(issue_question):
    issue_question.set_origin_id("101010")
    assert issue_question.email_id == None
    assert issue_question.issue_id == "101010"
    assert issue_question.comment_id == None
    assert issue_question.origin == "issue"  # make sure nothing changed here as well


def test_find_context_from_table(issue_question, test_db):
    # check db_for_tests for the dummy data
    dummy_issue_id = 1
    issue_question.set_origin_id(dummy_issue_id)
    issue_question.find_context_from_table(db=test_db)
    # 3 comments, we should see as context:
    correct_context = (
        "body of the first comment body of the second comment body of the third comment"
    )
    assert issue_question.context == correct_context
