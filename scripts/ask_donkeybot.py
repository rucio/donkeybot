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


def print_answers(answers):
    """
    Prints answers to query.
    """
    print("\nFINAL ANSWERS: (descending order)")
    for i, answer in enumerate(answers):
        print(f"Question: '{answer.user_question}'")
        # faq answers:
        if answer.origin == 'faq':
            print("FAQ answers: ")
            most_similar_faq_question = answer.metadata["most_similar_faq_question"]
            author = answer.metadata["author"]
            print(
                f"Answer: '{answer.extended_answer} \nMost similar FAQ question: {most_similar_faq_question}"
            )
            print(f"Author: {author}")
        elif answer.origin == 'documentation':
            url = answer.metadata["url"]
            print(f"Answer: '{answer.extended_answer} \nFor more info check: {url}")
            print(f"Confidence: {answer.confidence}")
        elif answer.origin == 'questions':
            most_similar_question = answer.metadata["most_similar_question"]
            print(
                f"Answer: '{answer.extended_answer} \nMost similar question: {most_similar_question}"
            )
            print(f"Confidence: {answer.confidence}")


def setup_search_engines(db=Database):
    print("Loading SearchEngines...")
    docs_se = SearchEngine()
    docs_se.load_index(db=db, table_name="rucio_doc_term_matrix")
    question_se = QuestionSearchEngine()
    question_se.load_index(db=db, table_name="questions_doc_term_matrix")
    faq_se = FAQSearchEngine()
    faq_se.load_index(db=db, table_name="faq_doc_term_matrix")
    return faq_se, docs_se, question_se


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""Use this script to ask DonkeyBot!"""
    )
    optional = parser.add_argument_group("optional arguments")

    optional.add_argument(
        "-m",
        "--model",
        default="distilbert-base-cased-distilled-squad",
        help="BERT/DistilBERT model used to inference answers. (default is distilbert-base-cased-distilled-squad)",
    )
    optional.add_argument(
        "-db",
        "--db_name",
        default="data_storage",
        help="Name of database where all data is stored. (default is data_storage)",
    )
    optional.add_argument(
        "-s",
        "--store_answers",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Store the answers on the '--answers_table' table. (default is False)",
    )
    optional.add_argument(
        "-n",
        "--num_answers_predicted_per_document",
        default=3,
        help="Number of answers predicted per document. (default is 3)",
    )
    optional.add_argument(
        "--answers_table",
        default="answers",
        help="Name of the answers table. (default is 'answers')",
    )

    args = parser.parse_args()
    db_name = args.db_name
    model = args.model
    answers_table = args.answers_table
    store_answers = args.store_answers
    num_answers_inf = int(args.num_answers_predicted_per_document)

    check_model_availability(model)

    # prepare data_storage
    data_storage = Database(f"{db_name}.db")
    # check for the answers table
    tables_in_db = list([table[0] for table in data_storage.get_tables()])
    if answers_table not in tables_in_db:
        print(f"Creating '{answers_table}' table in {db_name}.db")
        data_storage.create_answers_table(table_name=f"{answers_table}")

    # load answer detector
    print("Loading AnswerDetector...")
    gpu = 0 if torch.cuda.is_available() else -1
    answer_detector = AnswerDetector(
        model=model, device=gpu, num_answers_to_predict=num_answers_inf
    )

    # load search engines
    faq_se, docs_se, question_se = setup_search_engines(db=data_storage)

    # load interface
    qa_interface = QAInterface(
        detector=answer_detector,
        question_engine=question_se,
        faq_engine=faq_se,
        docs_engine=docs_se,
    )

    # Main Loop
    print("DonkeyBot ready to be asked!")
    try:
        while True:
            print("\nCTRL+C to exit donkeybot")
            query = str(input("ask question: "))
            top_k = int(input("how many answers: "))
            start_time = time.time()
            answers = qa_interface.get_answers(query, top_k=top_k)
            print(f"Total inference time: {round(time.time() - start_time, 2)} seconds")
            print_answers(answers)

            if store_answers:
                for answer in answers:
                    data_storage.insert_answer(answer, table_name=f"{answers_table}")
    except KeyboardInterrupt:
        data_storage.close_connection()
        sys.exit("\nExiting...")


if __name__ == "__main__":
    main()
