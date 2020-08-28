# bot modules
from bot.question.base import Question

# general python
import pytest


@pytest.fixture()
def test_question():
    question = Question(
        question_text="Did the test pass?",
        start_idx=0,
        end_idx=len("Did the test pass?"),
    )
    return question


def test_abstract_method_existance():
    assert "set_origin_id" in (Question.__abstractmethods__)
    assert "find_context_from_table" in (Question.__abstractmethods__)


def test_wrong_init():
    with pytest.raises(TypeError):
        question = Question()


def test_wrong_init_2():
    with pytest.raises(TypeError):
        question = Question(question_text="Did the test pass?")


def test_wrong_init_3():
    with pytest.raises(TypeError):
        question = Question(
            question_text="Did the test pass?",
            start_idx=0,
        )


def test_wrong_init_4():
    with pytest.raises(TypeError):
        question = Question(
            start_idx=0,
            end_idx=len("Did the test pass?"),
        )
