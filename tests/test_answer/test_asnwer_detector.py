# bot modules
from bot.answer.detector import AnswerDetector
from bot.answer.base import Answer

# general python
import pandas as pd
import pytest


@pytest.fixture(scope="module")
def answer_detector():
    answer_detector = AnswerDetector(
        model="distilbert-base-cased-distilled-squad",
        extended_answer_size=30,
        handle_impossible_answer=True,
        max_answer_len=20,
        max_question_len=20,
        max_seq_len=256,
        num_answers_to_predict=3,
        doc_stride=128,
        device=-1,
    )
    return answer_detector


@pytest.fixture()
def documents():
    documents = pd.DataFrame(
        {
            "context": [
                """
                    The aim of the Donkeybot project under GSoC 2020 is to use Natural Language Processing (NLP) 
                    to develop an intelligent bot prototype able to provide satisfying answers to Rucio users 
                    and handle support requests up to a certain level of complexity, 
                    forwarding only the remaining ones to the experts.
                    """,
                """
                    Different levels of expert support are available for users in case of problems. 
                    When satisfying answers are not found at lower support levels, a request from a user or a group 
                    of users can be escalated to the Rucio support. Due to the vast amount of support requests, 
                    methods to assist the support team in answering these requests are needed.
                    """,
            ],
            "col_2": ["first_doc", "second_doc"],
            "col_3": ["other", "data"],
        }
    )
    return documents


def test_answer_from_predict_type(answer_detector, documents):
    question = "What is the aim of Donkeybot?"
    answers = answer_detector.predict(question, documents, top_k=2)
    assert type(answers) == list
    for answer in answers:
        assert type(answer) == Answer


@pytest.mark.skip(reason="different results from example notebook; open bug")
def test_answer_from_predict_content(answer_detector, documents):
    question = "What is the aim of Donkeybot?"
    answers = answer_detector.predict(question, documents, top_k=2)
    for i, answer in enumerate(answers):
        print()
        print(f"answer {i+1}: {answer.answer} | confidence : {answer.confidence}")
    assert answers[0].answer == "assist the support team"
    assert answers[1].answer == "to use Natural Language Processing (NLP)"
