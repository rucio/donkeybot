# Here is the code for fetching the data through our different sources
# Whether that is github issues, Rucio documentation etc.
# The output is the raw form of the data that is used as input for the bot

# //TODO add some sort of authentication checking for the provided api token so that we dont insert bad data

# bot modules
import bot.helpers as helpers
import bot.config as config
from bot.database import Database
# general python
from abc import ABCMeta, abstractmethod
import string
import re
import warnings
import pandas as pd 
import numpy as np
from tqdm import tqdm
import sys


class IFetcher(metaclass=ABCMeta):
    """The Fetcher Interface"""
    @abstractmethod
    def fetch():
        """Fetches the data from their source"""
        pass

    @abstractmethod
    def save():
        """Saves the raw form of the fetched data."""
        pass

    @abstractmethod
    def load():
        """Loads the raw form of the fetched data."""
        pass


class FetcherFactory():

    @staticmethod
    def get_fetcher(data_type):
        try:
            if data_type == 'Issue':
                return IssueFetcher()
            if data_type == 'Documentation':
                return DocsFetcher()
            # Once email fetching is done, implementation will exist here
            if data_type == 'Email':
                return EmailFetcher()
            raise AssertionError("Fetcher not found")
        except AssertionError as _e:
            print(_e)


class IssueFetcher(IFetcher):
    
    def __init__(self):
        self.type = 'Github Issues Fetcher'
        pass


    def _check_repo(self):
        """Check that the GitHub repository is correct"""
        try:
            # if the request is correct then we have a TypeError (for ['message']) thus the try except block
            if helpers.request(self.issues_url, self.headers)['message'] == 'Not Found':
                raise InvalidRepoError(f"\nError: The repository is not in the correct format. Please use the format 'user/repo' et. 'rucio/rucio'.")
        except: 
            pass


    def fetch(self, repo, api_token, max_pages=201):
        """
        Return two pandas DataFrames that hold information for both
        issues and comments under said issues.
        Utilizes GitHub's Issues api.

        for issues   :
            number       : issue's number
            title        : issue's title
            state        : issue's state
            creator      : issue's creator
            comments     : number of comments in the issue
            body         : issue's body

        for comments :
            issue_number : issue's number that holds the comment
            comment_id   : comment's id
            creator      : comment's creator
            created_at   : date comment was created at
            body         : body of the comment 

        <!> Note : We haven't implemented api_token validation in my code
                   We expect the api_token to be correct, should get GitHub's errors if not
                   TODO Implement the above..

        :param max_pages    : max_pages requested through the api, default = 201
        :param repo         : GitHub repo (for us rucio/rucio) format `User/Repo` 
        :param api_token    : GitHub api token used for fetching the data
        """        

        self.max_pages = max_pages
        self.repo = repo
        self.api_token = api_token
        # headers sent with the GET request 
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'token {self.api_token}'} 
        # issues url for both open and closed issues 
        self.issues_url = f"https://api.github.com/repos/{self.repo}/issues?state=all"
        self._check_repo()
        
        # initialize the dataframes
        issues_df = pd.DataFrame(columns=['issue_id','title','state'
                                        , 'creator','comments','body'])
        comments_df = pd.DataFrame(columns=['issue_id', 'comment_id'
                                        , 'creator', 'created_at','body'])

        # starting from page 1 to avoid getting duplicate issues
        pages = range(1, self.max_pages) 
        print('fetching...')
        for page in tqdm(pages):
            for issue in helpers.request(self.issues_url + f'&page={page}', self.headers):
                if type(issue) == str:
                    # if the api_token is not correct, we are going to get an error on every issue
                    print(f"Error in issue {issue} moving on to the next...")
                    continue
                if '/pull/' in issue['html_url']:
                    # don't care about pull requests
                    continue

                # add comment data    
                issue_number = issue['number']
                issue_comments = issue['comments'] 
                if issue_comments != 0:
                    for comment in helpers.request(issue['comments_url'], self.headers):
                        if type(comment) == dict:
                            comment_id = comment['id']
                            comment_creator = comment['user']['login']
                            comment_created_at = comment['created_at']
                            comment_body = comment['body']

                            comments_df = comments_df.append({
                                'issue_id': issue_number,
                                'comment_id': comment_id,
                                'creator': comment_creator,
                                'created_at': comment_created_at,
                                'body': comment_body,
                                }, ignore_index=True)
                        else:
                            print(f"Error in issue {issue} on comment {comment}, moving on to the next...")
                            continue

                # add issue data
                issue_body = issue['body'].strip('/n/r') # strip for when its empty
                issue_title = issue['title']
                issue_state = issue['state']
                issue_creator = issue['user']['login']

                issues_df = issues_df.append({
                    'issue_id': issue_number,
                    'title': issue_title,
                    'state': issue_state,
                    'creator': issue_creator,
                    'comments': issue_comments,
                    'body': issue_body,
                    }, ignore_index=True)

        self.issues   = issues_df
        self.comments = comments_df    
        return issues_df, comments_df


    def save(self, db = Database, issues_table_name = 'issues', comments_table_name='issue_comments'):
        """
        Save the data in a .db file utilizing the bot.database.py sqlite wrapper

        : param db            : bot.database Database object 
        : issues_table_name   : name of the table where we'll store the issues
        : comments_table_name : name of the table where we'll store the comments
        """
        if all(hasattr(self, attr) for attr in ['issues', 'comments']):
            print('saving...')
            self.issues.to_sql(issues_table_name, con=db.db, if_exists='replace', index=False)
            self.comments.to_sql(comments_table_name, con=db.db, if_exists='replace', index=False)
        else:
            raise MissingDataFramesError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")


    def load(self, db = Database, issues_table_name = 'issues', comments_table_name='issue_comments'):
        """
        Load the data from the .db file.

        : param  db                  : bot.database Database object 
        : param  issues_table_name   : name of the table where we'll store the issues
        : param  comments_table_name : name of the table where we'll store the comments
        : return issues              : DataFrame holding the issues data
        : return comments            : DataFrame holding the comments data
        """
        try:
            print('loading...')
            self.issues = db.get_dataframe(f'{issues_table_name}').set_index('issue_id',drop=True)
            self.comments = db.get_dataframe(f'{comments_table_name}').set_index('comment_id',drop=True)
            return self.issues, self.comments
        except:
            raise MissingDataError(f"\nError: Data not found.")            

    
    # useful for anyone using the IssuesFetcher outside the scope of this project
    def load_with_pickle(self, repo):
        """ 
        Load the DataFrame stored in pickle file format.
        
        : param  repo                : name of the repository
        : return issues              : DataFrame holding the issues data
        : return comments            : DataFrame holding the comments data
        """
        try:
            print('loading...')
            repo_str = '_'.join(repo.split('/'))
            self.issues = pd.read_pickle(config.DATA_DIR + f"{repo_str}_issues.pkl")
            self.comments = pd.read_pickle(config.DATA_DIR + f"{repo_str}_comments.pkl")
            return self.issues, self.comments
        except:
            raise MissingDataError(f"\nError: Data not found.")            


    # useful for anyone using the IssuesFetcher outside the scope of this project
    def save_with_pickle(self):
        """Save the DataFrame in pickle file format."""
        if all(hasattr(self, attr) for attr in ['issues', 'comments']):
            print('saving...')
            repo_str = '_'.join(self.repo.split('/'))
            self.issues.to_pickle(config.DATA_DIR + f"{repo_str}_issues.pkl")
            self.comments.to_pickle(config.DATA_DIR + f"{repo_str}_comments.pkl")
        else:
            raise MissingDataFramesError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")
        

class InvalidRepoError(Exception):
    """Raised when the repository for the IssueFetcher is not correct."""
    pass

class MissingDataError(Exception):
    """Raised when the data we are trying to load isn't found."""
    pass

class MissingDataFramesError(Exception):
    """Raised when the dataframe(s) we are trying to save are missing."""
    pass


################################################################################################################################################
if __name__ == "__main__":
    # sample example for loading data we already created
    data_storage = Database('dataset_3.db')
    print("Let's create an IssuesFetcher")
    fetcher = FetcherFactory.get_fetcher('Issue')
    issues_df, comments_df = fetcher.load(db=data_storage, issues_table_name='issues', comments_table_name='issue_comments')
    print(issues_df.head())
    print(comments_df.head())    
