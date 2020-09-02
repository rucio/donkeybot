# bot modules
from bot.answer.base import Answer
from bot.database.sqlite import Database

# general python
import pytest


@pytest.fixture(scope="module")
def db_for_tests():
    db = Database("db_for_tests.db")
    yield db
    db.close_connection()


def test_user_question_ids_equality(db_for_tests):
    meta = {}
    meta["doc_id"] = 42
    meta["other_data"] = 23

    # only question is what we care about
    answers = []
    answer = Answer(
        question="WHAT?",
        model="superman",
        answer="that!",
        start=0,
        end=1,
        confidence="a+",
        extended_answer="what?->that!",
        extended_start=1,
        extended_end=23,
        metadata=meta,
    )
    answers.append(answer)

    answer = Answer(
        question="what?",
        model="superman",
        answer="that!",
        start=0,
        end=1,
        confidence="a+",
        extended_answer="what?->that!",
        extended_start=1,
        extended_end=23,
        metadata=meta,
    )
    answers.append(answer)

    answer = Answer(
        question="WHAT??????????",
        model="superman",
        answer="that!",
        start=0,
        end=1,
        confidence="a+",
        extended_answer="what?->that!",
        extended_start=1,
        extended_end=23,
        metadata=meta,
    )
    answers.append(answer)

    answer = Answer(
        question="WhAt ? ? ? ? ?",
        model="superman",
        answer="that!",
        start=0,
        end=1,
        confidence="a+",
        extended_answer="what?->that!",
        extended_start=1,
        extended_end=23,
        metadata=meta,
    )
    answers.append(answer)

    user_q_id = answers[0].user_question_id
    for answer in answers:
        assert answer.user_question_id == user_q_id
