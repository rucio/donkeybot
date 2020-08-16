# bot modules
from bot.parser.factory import ParserFactory
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""This is the script responsible for parsing GitHub issues"""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "-i",
        "--input_db",
        help="Input .db file name of the raw fetched issues",
        required=True,
    )
    optional.add_argument(
        "-o",
        "--output_db",
        default="data_storage",
        help="Output .db file name of the parsed issues (default is  data_storage)",
        required=True,
    )
    optional.add_argument(
        "--issues_table",
        default="issues",
        help="Name of the table where we will store the parsed issues and of the table where the raw issues are stored (default is issues)",
    )

    args = parser.parse_args()
    input_db = args.input_db
    output_db = args.output_db
    issues_table = args.issues_table

    # input
    raw_issues_data = Database(f"{input_db}.db").get_dataframe(issues_table)
    # output
    data_storage = Database(f"{output_db}.db")
    data_storage.create_issues_table(table_name=issues_table)
    # EmailParser
    print("Let's create an IssuesParser.")
    parser = ParserFactory.get_parser("Issue")
    parser.parse_dataframe(
        raw_issues_data, db=data_storage, issues_table_name=issues_table
    )
    print(f"Data from {input_db}.db parsed and saved on {output_db}.db")
    data_storage.close_connection()


if __name__ == "__main__":
    main()
