# bot modules
from bot.question.comments import CommentQuestion
from bot.database.sqlite import Database

# general python
import pytest


@pytest.fixture
def comment_question():
    question = CommentQuestion(
        question_text="Did the test pass?", start_idx=0, end_idx=18
    )
    return question


@pytest.fixture(scope="module")
def test_db():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


def test_attribute_error_when_set_origin_id_not_used(comment_question):
    with pytest.raises(AttributeError):
        comment_question.email_id
    with pytest.raises(AttributeError):
        comment_question.issue_id
    with pytest.raises(AttributeError):
        comment_question.comment_id


def test_origin_of_comment_question(comment_question):
    assert comment_question.origin == "comment"


def test_set_origin_id(comment_question):
    comment_question.set_origin_id("101010")
    assert comment_question.email_id == None
    assert comment_question.issue_id == None
    assert comment_question.comment_id == "101010"
    assert comment_question.origin == "comment"  # make sure nothing changed here as well


def test_find_context_from_table(comment_question, test_db):
    # check db_for_tests for the dummy data
    dummy_issue_id = 1
    comment_question.set_origin_id(dummy_issue_id)
    comment_question.find_context_from_table(db=test_db)
    # 3 comments, ours is number 1, we should see as context:
    correct_context = "body of the second comment body of the third comment"
    assert comment_question.context == correct_context
