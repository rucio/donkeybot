# bot modules
from bot.brain import QAInterface
from bot.searcher.question import QuestionSearchEngine
from bot.searcher.base import SearchEngine
from bot.searcher.faq import FAQSearchEngine
from bot.answer.detector import AnswerDetector
from bot.database.sqlite import Database

# general python
import pytest


@pytest.fixture(scope="module")
def db_for_tests():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


@pytest.fixture(scope="module")
def faq_se(db_for_tests):
    faq_se = FAQSearchEngine()
    faq_se.create_index(db=db_for_tests)
    return faq_se


def test_qa_interface_check_detector():
    with pytest.raises(SystemExit):
        QAInterface(
            detector="not an AnswerDetector",
            question_engine=QuestionSearchEngine,
            faq_engine=FAQSearchEngine,
            docs_engine=SearchEngine,
        )


def test_qa_interface_check_engines_quest_se():
    with pytest.raises(SystemExit):
        QAInterface(
            detector=AnswerDetector,
            question_engine="not a QuestionSearchEngine",
            faq_engine=FAQSearchEngine,
            docs_engine=SearchEngine,
        )


def test_qa_interface_check_engines_faq_se():
    with pytest.raises(SystemExit):
        QAInterface(
            detector=AnswerDetector,
            question_engine=QuestionSearchEngine,
            faq_engine="not an FAQSearchEngine",
            docs_engine=SearchEngine,
        )


def test_qa_interface_check_engines_docs_se():
    with pytest.raises(SystemExit):
        QAInterface(
            detector=AnswerDetector,
            question_engine=QuestionSearchEngine,
            faq_engine=FAQSearchEngine,
            docs_engine="not a SearchEngine",
        )
