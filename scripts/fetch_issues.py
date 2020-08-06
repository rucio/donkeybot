# bot modules
from bot.fetcher.factory import FetcherFactory
from bot.database.sqlite import Database

# general python
import pandas as pd
import argparse

def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for fetching GitHub issues and comments''')
    required = parser.add_argument_group('required arguments')
    optional = parser.add_argument_group('optional arguments')
    
    
    required.add_argument(
        '-r',
        '--repo',
        help='Name of the GitHub repository we are fetching from. Format `user/repo`',
        required=True)
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
        '-max_pages',
        '--max_pages',
        default=201,
        type=int,
        help='Maximum number of pages we will request through GitHubs api (default is 201)',
        required=False)
    optional.add_argument(
        '-issues_table',
        '--issues_table',
        default='issues',
        help='Name of the table where we will store the issues (default is issues)')
    optional.add_argument(
        '-comments_table',
        '--comments_table',
        default='issue_comments',
        help='Name of the table where we will store the comments (default is issue_comments)')
    
    args = parser.parse_args()
    db_name = args.database
    repository = args.repo
    token = args.token
    issues_table = args.issues_table
    comments_table = args.comments_table
    max_pages = args.max_pages

    # IssueFetcher 
    data_storage = Database(f'{db_name}.db')
    fetcher = FetcherFactory.get_fetcher('Issue')
    (issues_df, comments_df) = fetcher.fetch(repo=repository, api_token=token, max_pages=max_pages)
    fetcher.save(db=data_storage, issues_table_name=issues_table, comments_table_name=comments_table)
    print(f"Data saved on {db_name}.db")
    print("Sample:")
    print("Issues")
    print(issues_df.head())
    print("Comments")
    print(comments_df.head())    
    data_storage.close_connection()

if __name__ == '__main__':
    main()

