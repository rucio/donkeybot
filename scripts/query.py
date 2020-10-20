# bot modules
from bot.searcher.base import SearchEngine
from bot.searcher.question import QuestionSearchEngine
from bot.database.sqlite import Database
from bot.utils import str2bool, check_positive

# general python
import pandas as pd
import argparse
import sys


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""With this script you can query with the Search Engine module and get top-k results."""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")
    required.add_argument(
        "-q",
        "--query",
        help="What you want to query.",
        required=True,
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
            print(docs_results[["doc_id", "question", "name", "context"]])
        if match_questions:
            question_results = q_se.search(query, top_k)
            print(f"\nTop-{top_k} retrieved past questions:")
            print(question_results[["question_id", "query", "question", "context"]])

    except Exception as _e:
        print("Error : ", end="")
        sys.exit(_e)


if __name__ == "__main__":
    main()
