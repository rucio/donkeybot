# bot modules
from bot.fetchers import FetcherFactory
from bot.database import Database

# general python
import pandas as pd
import argparse

def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for fetching the Rucio documentation through GitHub''')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    
    required.add_argument(
        '-t',
        '--token',
        help='GitHub api token to be used for the GET requests while fetching',
        required=True)
    optional.add_argument(
        '-db',
        '--database',
        default='dataset',
        help='Output .db file where the data is stored (default is dataset)',
        )
    optional.add_argument(
        '--documentation_table',
        default='docs',
        help='Name of the table where we will store the documentation (default is docs)')
    
    args = parser.parse_args()
    db_name = args.database
    token = args.token
    docs_table = args.documentation_table

    # IssueFetcher 
    data_storage = Database(f'{db_name}.db')
    fetcher = FetcherFactory.get_fetcher('Rucio Documentation')
    docs_df = fetcher.fetch(api_token=token)
    fetcher.save(db=data_storage, docs_table_name=docs_table)
    print(f"Data saved on {db_name}.db")
    print("Sample docs:")
    print(docs_df.head())

if __name__ == '__main__':
    main()

