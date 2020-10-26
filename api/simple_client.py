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


class SimpleClient:
    """
    A prototype of a client to comunicate with donkeybot.
    :param model: NLP model, e.g. BERT.
    :param data_storage: db where data is stored.
    :param num_answers_inf: number of highest score answers that client work with.

    """
    def __init__(self, model=None, db_name="data_storage", num_answers_inf=1):
  
        self.model = "distilbert-base-cased-distilled-squad"
        if model:
            check_model_availability(model)
            self.model = model

        gpu = 0 if torch.cuda.is_available() else -1
        self.answer_detector = AnswerDetector(model=self.model,
                                             device=gpu,
                                             num_answers_to_predict=num_answers_inf
                                            )
        data_storage = Database(f"{db_name}.db")
        faq_se, docs_se, question_se = setup_search_engines(db=data_storage)
        self.qa_interface = QAInterface(detector=self.answer_detector,
                                        question_engine=question_se,
                                        faq_engine=faq_se,
                                        docs_engine=docs_se)


    def get_answer(self, question):
        answers = self.qa_interface.get_answers(question, top_k=1)
        for i, answer in enumerate(answers):
            #TODO
            return answer.extended_answer, answer.confidence
