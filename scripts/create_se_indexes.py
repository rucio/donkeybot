# bot modules
from bot.searcher.base import SearchEngine
from bot.searcher.question import QuestionSearchEngine
from bot.database.sqlite import Database

# general python
import argparse


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""This script indexes our data for SearchEngine and QuestionSearchEngine."""
    )
    optional = parser.add_argument_group("optional arguments")

    optional.add_argument(
        "-db",
        "--db_name",
        default="data_storage",
        help="Database name of our storage. (default is data_storage)",
    )
    optional.add_argument(
        "--documentation_table",
        default="docs",
        help="Name of the table where the documentation is stored (default is docs)",
    )
    optional.add_argument(
        "--questions_table",
        default="questions",
        help="Name given to the table holding the questions. (default is questions)",
    )

    args = parser.parse_args()
    db_name = args.db_name
    docs_table = args.documentation_table
    questions_table = args.questions_table

    data_storage = Database(f"{db_name}.db")

    # Documentation SearchEngine
    docs_se = SearchEngine()
    docs_df = data_storage.get_dataframe(docs_table)
    # let's not index the release-notes in this version of the bot
    # this code also exists is load_index() for rucio documents
    docs_df = docs_df[docs_df["doc_type"] != "release_notes"]
    print("Indexing Rucio documentation for the SearchEngine...")
    docs_se.create_index(
        corpus=docs_df, db=data_storage, table_name="rucio_doc_term_matrix"
    )

    # QuestionSearchEngine
    questions_se = QuestionSearchEngine()
    questions_df = data_storage.get_dataframe(questions_table)
    print("Indexing questions for the QuestionSearchEngine...")
    questions_se.create_index(
        corpus=questions_df, db=data_storage, table_name="questions_doc_term_matrix"
    )


if __name__ == "__main__":
    main()
