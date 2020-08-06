# bot modules
from bot.parser.factory import ParserFactory
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse

def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for parsing the emails''')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    required.add_argument(
        '-i',
        '--input_db',
        help='Input .db file name of the raw emails',
        required=True)
    optional.add_argument(
        '-o',
        '--output_db',
        default='data_storage',
        help='Output .db file name of the parsed emails (default is  data_storage)',
        required=True)
    optional.add_argument(
        '--emails_table',
        default='emails',
        help='Name of the table where we will store the parsed emails and of the table where the raw emails are stored (default is emails)')
    
    args = parser.parse_args()
    input_db = args.input_db
    output_db = args.output_db
    emails_table = args.emails_table

    # input
    raw_emails_data = Database(f'{input_db}.db').get_dataframe(emails_table)
    # output
    data_storage = Database(f'{output_db}.db')
    data_storage.create_emails_table(table_name=emails_table)
    # EmailParser 
    print("Let's create an EmailParser")
    parser = ParserFactory.get_parser('Email')
    parser.parse_dataframe(raw_emails_data, db=data_storage, emails_table_name=emails_table)
    print(f"Data from {input_db}.db parsed and saved on {output_db}.db")
    data_storage.close_connection()


if __name__ == '__main__':
    main()

