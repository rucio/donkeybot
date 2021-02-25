# This script can be used to ask DonkeyBot a question.
# There are many more parameters we can tweak and change for both the search engines
# and the answer detector. For the purpose of this demo we stick to the default values.
# For more information refer to the source code and the documentation

# bot modules
from bot.brain import QAInterface
from bot.searcher.base import SearchEngine
from bot.searcher.question import QuestionSearchEngine
from bot.searcher.faq import FAQSearchEngine
from bot.answer.detector import AnswerDetector
from bot.database.sqlite import Database
from bot.utils import check_positive, str2bool
from bot.config import MODELS_DIR

# general python
import time
import torch
import os.path
import sys
import argparse


def check_model_availability(model):
    """Assert that all the model files exist in the MODELS_DIR"""
    try:
        assert os.path.isfile(MODELS_DIR + model + "\\config.json") == True
        assert os.path.isfile(MODELS_DIR + model + "\\pytorch_model.bin") == True
        assert os.path.isfile(MODELS_DIR + model + "\\special_tokens_map.json") == True
        assert os.path.isfile(MODELS_DIR + model + "\\tokenizer_config.json") == True
        assert os.path.isfile(MODELS_DIR + model + "\\vocab.txt") == True
    except AssertionError as _e:
        print(
            f"Error: Make sure that the model is correct and exists in '{MODELS_DIR}'."
        )
        sys.exit(_e)


def setup_search_engines(db=Database):
    print("Loading SearchEngines...")
    docs_se = SearchEngine()
    docs_se.load_index(db=db, table_name="rucio_doc_term_matrix")
    question_se = QuestionSearchEngine()
    question_se.load_index(db=db, table_name="questions_doc_term_matrix")
    faq_se = FAQSearchEngine()
    faq_se.load_index(db=db, table_name="faq_doc_term_matrix")
    return faq_se, docs_se, question_se


class Donkeybot:
    """
    A wrapper for Donkeybot to be used by the server for the slackbot.
    Usability same with ask_donkeybot.py CLI scipt.

    :param model: NLP model, e.g. distilbert-base-cased-distilled-squad.
    :param data_storage: db where data is stored.
    :param num_answers_to_predict: number of answers predicted per document looked at.
    """

    def __init__(self, model=None, db_name="data_storage", num_answers_to_predict=3):

        self.model = "distilbert-base-cased-distilled-squad"
        if model:
            check_model_availability(model)
            self.model = model

        # better if just CPU for inference
        gpu = 0 if torch.cuda.is_available() else -1
        self.answer_detector = AnswerDetector(
            model=self.model, device=gpu, num_answers_to_predict=num_answers_to_predict
        )
        self.data_storage = Database(f"{db_name}.db")
        faq_se, docs_se, question_se = setup_search_engines(db=self.data_storage)
        self.qa_interface = QAInterface(
            detector=self.answer_detector,
            question_engine=question_se,
            faq_engine=faq_se,
            docs_engine=docs_se,
        )

    def get_answers(self, question, top_k=1, store_answers=False):
        """Search past questions table for an answer"""
        answers = self.qa_interface.get_answers(question, top_k=top_k)
        # TODO add confidence cutoff
        if store_answers:
            for answer in answers:
                self.data_storage.insert_answer(answer, table_name=f"{answers_table}")
        return answers

    def get_faq_answers(self, question, num_faqs=1, store_answers=False):
        """Search FAQs for an answer"""
        answers = self.qa_interface.get_faq_answers(question, num_faqs=num_faqs)
        if store_answers:
            for answer in answers:
                self.data_storage.insert_answer(answer, table_name=f"{answers_table}")
        return answers
