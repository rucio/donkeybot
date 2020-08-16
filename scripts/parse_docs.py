# bot modules
from bot.parser.factory import ParserFactory
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""This is the script responsible for parsing Rucio Documentation"""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "-i",
        "--input_db",
        help="Input .db file name of the raw fetched docs",
        required=True,
    )
    optional.add_argument(
        "-o",
        "--output_db",
        default="data_storage",
        help="Output .db file name of the parsed docs (default is data_storage)",
        required=True,
    )
    optional.add_argument(
        "--docs_table",
        default="docs",
        help="Name of the table where we will store the parsed docs and of the table where the raw docs_table are stored (default is docs)",
    )

    args = parser.parse_args()
    input_db = args.input_db
    output_db = args.output_db
    docs_table = args.docs_table

    # input
    raw_docs_data = Database(f"{input_db}.db").get_dataframe(docs_table)
    # output
    data_storage = Database(f"{output_db}.db")
    data_storage.create_docs_table(table_name=docs_table)
    # EmailParser
    print("Let's create an RucioDocsParser.")
    parser = ParserFactory.get_parser("Rucio Documentation")
    parser.parse_dataframe(raw_docs_data, db=data_storage, docs_table_name=docs_table)
    print(f"Data from {input_db}.db parsed and saved on {output_db}.db")
    data_storage.close_connection()


if __name__ == "__main__":
    main()
