# bot modules
from bot.searcher.base import SearchEngine
from bot.searcher.question import QuestionSearchEngine
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse
import sys


def str2bool(v):
    """Used to convert string to boolean"""
    if isinstance(v, bool):
        return v
    if v.lower() in ("yes", "true", "t", "y", "1"):
        return True
    elif v.lower() in ("no", "false", "f", "n", "0"):
        return False
    else:
        raise argparse.ArgumentTypeError("Boolean value expected.")


def check_positive(value):
    """Used to check that the value of the argument is a positive integer"""
    ivalue = int(value)
    if ivalue <= 0:
        raise argparse.ArgumentTypeError("%s is an invalid positive int value" % value)
    return ivalue


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""With this script you can query with the Search Engine module and get top-k results."""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")
    required.add_argument(
        "-q", "--query", help="What you want to query.", required=True,
    )
    required.add_argument(
        "-k",
        "--top_k",
        type=check_positive,
        help="Number of documents that'll be retrieved.",
        required=True,
    )
    optional.add_argument(
        "-mq",
        "--match_questions",
        type=str2bool,
        nargs="?",  # 0 or 1 argument
        const=True,
        default=False,
        help="Match query to similar questions.",
    )
    optional.add_argument(
        "-md",
        "--match_docs",
        type=str2bool,
        nargs="?",
        const=True,
        default=False,
        help="Match query to similar documents.",
    )
    optional.add_argument(
        "--docs_index",
        default="rucio_doc_term_matrix",
        help="Name of documentation index column. (default is rucio_doc_term_matrix)",
    )
    optional.add_argument(
        "--docs_original_table",
        default="docs",
        help="Name of the original table for the documentation. (default is docs)",
    )
    optional.add_argument(
        "--question_index",
        default="questions_doc_term_matrix",
        help="Name of questions index column. (default is questions_doc_term_matrix)",
    )
    optional.add_argument(
        "--questions_original_table",
        default="questions",
        help="Name of the original table for the questions. (default is questions)",
    )
    optional.add_argument(
        "-db",
        "--db_name",
        default="data_storage",
        help="Name of database where indexes are stored. (default is data_storage)",
    )

    args = parser.parse_args()
    db_name = args.db_name
    query = args.query
    top_k = int(args.top_k)
    if not (args.match_questions or args.match_docs):
        parser.error(
            "No index to search requested, add -mq/--match_questions or -md/--match_docs"
        )
    match_questions = args.match_questions
    match_docs = args.match_docs
    docs_idx_name = args.docs_index
    docs_original_table = args.docs_original_table
    question_original_table = args.questions_original_table
    question_idx_name = args.question_index

    data_storage = Database(f"{db_name}.db")
    # load SE's
    try:
        docs_se = SearchEngine()
        docs_se.load_index(
            db=data_storage,
            table_name=docs_idx_name,
            original_table=docs_original_table,
        )
        q_se = QuestionSearchEngine()
        q_se.load_index(
            db=data_storage,
            table_name=question_idx_name,
            original_table=question_original_table,
        )
        data_storage.close_connection()
        if match_docs:
            docs_results = docs_se.search(query, top_k)
            print(f"\nTop-{top_k} retrieved documentation:")
            print(docs_results[["question", "name", "context"]])
        if match_questions:
            question_results = q_se.search(query, top_k)
            print(f"\nTop-{top_k} retrieved past questions:")
            print(question_results[["query", "question", "context"]])

    except Exception as _e:
        print("Error : ", end="")
        sys.exit(_e)


if __name__ == "__main__":
    main()