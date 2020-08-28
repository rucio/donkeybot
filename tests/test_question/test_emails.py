# bot modules
from bot.question.emails import EmailQuestion
from bot.database.sqlite import Database

# general python
import pytest


@pytest.fixture
def email_question():
    question = EmailQuestion(
        question_text="Did the test pass?", start_idx=0, end_idx=18
    )
    return question


@pytest.fixture(scope="module")
def test_db():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


def test_attribute_error_when_set_origin_id_not_used(email_question):
    with pytest.raises(AttributeError):
        email_question.email_id
    with pytest.raises(AttributeError):
        email_question.issue_id
    with pytest.raises(AttributeError):
        email_question.comment_id


def test_origin_of_email_question(email_question):
    assert email_question.origin == "email"


def test_set_origin_id(email_question):
    email_question.set_origin_id("101010")
    assert email_question.email_id == "101010"
    assert email_question.issue_id == None
    assert email_question.comment_id == None
    assert email_question.origin == "email"  # make sure nothing changed here as well


def test_find_context_from_table(email_question, test_db):
    # check db_for_tests for the dummy data
    dummy_email_id = 1
    email_question.set_origin_id(dummy_email_id)
    email_question.find_context_from_table(db=test_db)
    # 2 emails in reply chain, we should see the body of the 2nd as context
    correct_context = "Hey from email 2 body "
    assert email_question.context == correct_context
