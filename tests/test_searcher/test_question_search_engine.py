# bot modules
from bot.searcher.question import QuestionSearchEngine

# general python
import pytest


def test_default_index_for_questions():
    se = QuestionSearchEngine()
    assert se.column_to_index == ["question"]


def test_default_ids_for_questions():
    se = QuestionSearchEngine()
    assert se.document_ids_name == "question_id"


def test_type_for_questions():
    se = QuestionSearchEngine()
    assert se.type == "Question Search Engine"


@pytest.mark.skip(reason="need to look at attach_qa_data closer")
def test_base_attach_qa_data(dummy_email_se, test_db):
    pass


@pytest.mark.skip(reason="look into how to test")
def test_create_index():
    pass


@pytest.mark.skip(reason="look into how to test")
def test_load_index():
    pass
