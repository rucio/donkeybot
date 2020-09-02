# bot modules
from bot.searcher.faq import FAQSearchEngine

# general python
import pytest


def test_default_index_for_faqs():
    se = FAQSearchEngine()
    assert se.column_to_index == ["keywords", "question"]


def test_default_ids_for_faqs():
    se = FAQSearchEngine()
    assert se.document_ids_name == "faq_id"


def test_type_for_faqs():
    se = FAQSearchEngine()
    assert se.type == "FAQ Search Engine"


@pytest.mark.skip(reason="need to look at attach_qa_data closer")
def test_base_attach_qa_data(dummy_email_se, test_db):
    pass


@pytest.mark.skip(reason="look into how to test")
def test_create_index():
    pass


@pytest.mark.skip(reason="look into how to test")
def test_load_index():
    pass
