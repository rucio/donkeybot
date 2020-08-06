# bot modules
from bot.parsers import ParserFactory
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse

def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for parsing GitHub issue comments''')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    required.add_argument(
        '-i',
        '--input_db',
        help='Input .db file name of the raw fetched issue comments',
        required=True)
    optional.add_argument(
        '-o',
        '--output_db',
        default='data_storage',
        help='Output .db file name of the parsed issues (default is  data_storage)',
        required=True)
    optional.add_argument(
        '--issue_comments_table',
        default='issue_comments',
        help='Name of the table where we will store the parsed issues and of the table where the raw issue comments are stored (default is issue_comments)')
    
    args = parser.parse_args()
    input_db = args.input_db
    output_db = args.output_db
    issue_comments_table = args.issue_comments_table

    # input
    raw_issue_comments_data = Database(f'{input_db}.db').get_dataframe(issue_comments_table)
    # output
    data_storage = Database(f'{output_db}.db')
    data_storage.create_issue_comments_table(table_name=issue_comments_table)
    # EmailParser 
    print("Let's create an IssueCommentsParser.")
    parser = ParserFactory.get_parser('Issue Comment')
    parser.parse_dataframe(raw_issue_comments_data, db=data_storage, issue_comments_table=issue_comments_table)
    print(f"Data from {input_db}.db parsed and saved on {output_db}.db")
    data_storage.close_connection()


if __name__ == '__main__':
    main()

