
# bot modules
import bot.utils as utils
import bot.config as config
from bot.database.sqlite import Database
from bot.fetcher.interface import IFetcher,LoadingError,\
                                  SavingError,InvalidRepoError,\
                                  InvalidTokenError
# general python
import string
import re
import pandas as pd 
import numpy as np
from tqdm import tqdm
import sys

class IssueFetcher(IFetcher):
    
    def __init__(self):
        self.type = 'Github Issues Fetcher'
        return

    def _check_repo(self):
        """Check that the GitHub repository is correct"""
        try:
            # if the request is correct then no message is returned and we have a TypeError
            if utils.request(self.issues_url, self.headers)['message'] == 'Not Found':
                raise InvalidRepoError(f"\nError: The repository is not in the correct format. Please use the format 'user/repo' eg. 'rucio/rucio'.")
        except InvalidRepoError as _e: 
            sys.exit(_e)
        except:
            # we don't care about the TypeError
            pass

    def _check_token(self):
        """Check if the GitHub token is correct"""
        try:
            # if the request is correct then no message is returned and we have a TypeError
            if utils.request(self.issues_url, self.headers)['message'] == 'Bad credentials':
                raise InvalidTokenError(f"\nError: Bad credentials. The OAUTH token {self.api_token} is not correct.")
        except InvalidTokenError as _e: 
            sys.exit(_e)
        except: 
            # we don't care about the TypeError
            pass       

    def fetch(self, repo, api_token, max_pages=201):
        """
        Return two pandas DataFrames that hold information for both
        issues and comments under said issues.
        Utilizes GitHub's Issues api.

        for issues   :
            issue_id     : issue's number
            title        : issue's title
            state        : issue's state
            creator      : issue's creator
            created_at   : date comment was created at
            comments     : number of comments in the issue
            body         : issue's body

        for comments :
            issue_id     : issue's number that holds the comment
            comment_id   : comment's id
            creator      : comment's creator
            created_at   : date comment was created at
            body         : body of the comment 

        :param max_pages    : max_pages requested through the api, default = 201
        :param repo         : GitHub repo (for us rucio/rucio) format `User/Repo` 
        :param api_token    : GitHub api token used for fetching the data
        :return issues_df   : DataFrame containing information for the issues
        :return comments_df : DataFrame containing information for the comments
        """        
        self.max_pages = max_pages
        self.repo = repo
        self.api_token = api_token
        # headers sent with the GET request 
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'token {self.api_token}'} 
        # issues url for both open and closed issues 
        self.issues_url = f"https://api.github.com/repos/{self.repo}/issues?state=all"
        self._check_repo()
        self._check_token()

        # initialize the dataframes
        issues_df   = pd.DataFrame(columns=['issue_id','title','state'
                                        , 'creator', 'created_at','comments','body'])
        comments_df = pd.DataFrame(columns=['issue_id', 'comment_id'
                                        , 'creator','created_at','body'])

        # starting from page 1 to avoid getting duplicate issues
        pages = range(1, self.max_pages) 
        print('Fetching...')
        for page in tqdm(pages):
            for issue in utils.request(self.issues_url + f'&page={page}', self.headers):
                if type(issue) == str:
                    # if the api_token is not correct, we are going to get an error on every issue
                    print(f"Error: Problem fetching issue {issue} moving on to the next...")
                    continue
                if '/pull/' in issue['html_url']:
                    # don't care about pull requests
                    continue

                # add comment data    
                issue_number   = issue['number']
                issue_comments = issue['comments'] 
                if issue_comments != 0:
                    for comment in utils.request(issue['comments_url'], self.headers):
                        if type(comment) == dict:
                            comment_id         = comment['id']
                            comment_creator    = comment['user']['login']
                            comment_created_at = comment['created_at']
                            comment_body       = comment['body']

                            comments_df = comments_df.append({
                                'issue_id'   : issue_number,
                                'comment_id' : comment_id,
                                'creator'    : comment_creator,
                                'created_at' : comment_created_at,
                                'body'       : comment_body,
                                }, ignore_index=True)
                        else:
                            print(f"Error: Problem fetching issue {issue} on comment {comment}, moving on to the next...")
                            continue

                # add issue data
                issue_body       = issue['body'].strip('/n/r') # strip for when its empty
                issue_title      = issue['title']
                issue_state      = issue['state']
                issue_creator    = issue['user']['login']
                issue_created_at = issue['created_at']

                issues_df = issues_df.append({
                    'issue_id'   : issue_number,
                    'title'      : issue_title,
                    'state'      : issue_state,
                    'creator'    : issue_creator,
                    'created_at' : issue_created_at,
                    'comments'   : issue_comments,
                    'body'       : issue_body,
                    }, ignore_index=True)

        self.issues   = issues_df
        self.comments = comments_df    
        return issues_df, comments_df

    def save(self, db = Database, issues_table_name = 'issues', comments_table_name='issue_comments'):
        """
        Save the data in a .db file utilizing our sqlite wrapper

        : param db            : bot.database.sqlite Database object 
        : issues_table_name   : name of the table where we'll store the issues
        : comments_table_name : name of the table where we'll store the comments
        """
        if all(hasattr(self, attr) for attr in ['issues', 'comments']):
            print('Saving...')
            self.issues.to_sql(issues_table_name, con=db.db, if_exists='replace', index=False)
            self.comments.to_sql(comments_table_name, con=db.db, if_exists='replace', index=False)
        else:
            raise SavingError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")

    def load(self, db = Database, issues_table_name = 'issues', comments_table_name='issue_comments'):
        """
        Load the data from the .db file.

        : param  db                  : bot.database.sqlite Database object 
        : param  issues_table_name   : name of the table where we'll store the issues
        : param  comments_table_name : name of the table where we'll store the comments
        : return issues              : DataFrame holding the issues data
        : return comments            : DataFrame holding the comments data
        """
        try:
            print('Loading...')
            self.issues = db.get_dataframe(f'{issues_table_name}')
            self.comments = db.get_dataframe(f'{comments_table_name}')
            return self.issues, self.comments
        except:
            raise LoadingError(f"\nError: Data not found.")            
            
    # useful for anyone using the IssuesFetcher outside the scope of this project
    def save_with_pickle(self):
        """Save the DataFrame in pickle file format."""
        if all(hasattr(self, attr) for attr in ['issues', 'comments']):
            print('Saving...')
            repo_str = '_'.join(self.repo.split('/'))
            self.issues.to_pickle(config.DATA_DIR + f"{repo_str}_issues.pkl")
            self.comments.to_pickle(config.DATA_DIR + f"{repo_str}_comments.pkl")
        else:
            raise SavingError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")
        
    # useful for anyone using the IssuesFetcher outside the scope of this project
    def load_with_pickle(self, repo):
        """ 
        Load the DataFrame stored in pickle file format.
        
        : param  repo       : name of the repository
        : return issues     : DataFrame holding the issues data
        : return comments   : DataFrame holding the comments data
        """
        try:
            print('Loading...')
            repo_str = '_'.join(repo.split('/'))
            self.issues = pd.read_pickle(config.DATA_DIR + f"{repo_str}_issues.pkl")
            self.comments = pd.read_pickle(config.DATA_DIR + f"{repo_str}_comments.pkl")
            return self.issues, self.comments
        except:
            raise LoadingError(f"\nError: Data not found.")       

if __name__ == '__main__':
    pass