# Here is the code for fetching the data through our different sources
# Whether that is github issues, Rucio documentation etc.
# The output is the raw form of the data that is used as input for the bot

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
import requests


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
            if data_type == 'Rucio Documentation':
                return RucioDocsFetcher()
            # Once email ftching is done, implementation will exist here
            if data_type == 'Email':
                return EmailFetcher()
            raise AssertionError("Fetcher not found")
        except AssertionError as _e:
            print(_e)


class IssueFetcher(IFetcher):
    
    def __init__(self):
        self.type = 'Github Issues Fetcher'
        return


    def _check_repo(self):
        """Check that the GitHub repository is correct"""
        try:
            # if the request is correct then no message is returned and we have a TypeError
            if helpers.request(self.issues_url, self.headers)['message'] == 'Not Found':
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
            if helpers.request(self.issues_url, self.headers)['message'] == 'Bad credentials':
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
            issue_id       : issue's number
            title        : issue's title
            state        : issue's state
            creator      : issue's creator
            comments     : number of comments in the issue
            body         : issue's body

        for comments :
            issue_id : issue's number that holds the comment
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
                                        , 'creator','comments','body'])
        comments_df = pd.DataFrame(columns=['issue_id', 'comment_id'
                                        , 'creator','created_at','body'])

        # starting from page 1 to avoid getting duplicate issues
        pages = range(1, self.max_pages) 
        print('Fetching...')
        for page in tqdm(pages):
            for issue in helpers.request(self.issues_url + f'&page={page}', self.headers):
                if type(issue) == str:
                    # if the api_token is not correct, we are going to get an error on every issue
                    print(f"Error: Problem fetching issue {issue} moving on to the next...")
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
                            comment_id         = comment['id']
                            comment_creator    = comment['user']['login']
                            comment_created_at = comment['created_at']
                            comment_body       = comment['body']

                            comments_df = comments_df.append({
                                'issue_id': issue_number,
                                'comment_id': comment_id,
                                'creator': comment_creator,
                                'created_at': comment_created_at,
                                'body': comment_body,
                                }, ignore_index=True)
                        else:
                            print(f"Error: Problem fetching issue {issue} on comment {comment}, moving on to the next...")
                            continue

                # add issue data
                issue_body    = issue['body'].strip('/n/r') # strip for when its empty
                issue_title   = issue['title']
                issue_state   = issue['state']
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
            print('Saving...')
            self.issues.to_sql(issues_table_name, con=db.db, if_exists='replace', index=False)
            self.comments.to_sql(comments_table_name, con=db.db, if_exists='replace', index=False)
        else:
            raise SavingError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")


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
        
        : param  repo                : name of the repository
        : return issues              : DataFrame holding the issues data
        : return comments            : DataFrame holding the comments data
        """
        try:
            print('Loading...')
            repo_str = '_'.join(repo.split('/'))
            self.issues = pd.read_pickle(config.DATA_DIR + f"{repo_str}_issues.pkl")
            self.comments = pd.read_pickle(config.DATA_DIR + f"{repo_str}_comments.pkl")
            return self.issues, self.comments
        except:
            raise LoadingError(f"\nError: Data not found.")            


   



class RucioDocsFetcher(IFetcher):
    """Only for Rucio's documentation."""
    
    def __init__(self):
        self.type = 'Rucio Documentation Fetcher'
        self.repo = 'rucio/rucio'
        self.docs_url = f'https://api.github.com/repos/{self.repo}/contents/doc/source'
        # root_download_url + filepath gives us the raw form of the data in a file
        # eg. root_download_url + '/doc/source/man/daemons.rst' 
        self.root_download_url = 'https://raw.githubusercontent.com/rucio/rucio/master'
        return


    def _check_token(self):
        """Check if the GitHub token is correct"""
        try:
            # if the request is correct then no message is returned and we have a TypeError
            if helpers.request(self.docs_url, self.headers)['message'] == 'Bad credentials':
                raise InvalidTokenError(f"\nError: Bad credentials. The OAUTH token {self.api_token} is not correct.")
        except InvalidTokenError as _e: 
            sys.exit(_e)
        except: 
            # we don't care about the TypeError
            pass       


    def _extract_daemon_body(self, body):
        """
        Parses the body of the daemon documentation under doc/source/man/
        to
        1) find patterns like                 
                .. argparse::
                :filename: bin/rucio-bb8
                :func: get_parser
                :prog: rucio-bb8

        2) tHen move to the appropriate path and match two regexes
            - One that matches the description content for each daemon
            - One the epilog content for each daemon
            (more info under config.py)

        If the above pattern doesn't match we simply return the initial body.
            
        : param body        : initial, raw daemon documentation body under doc/source/man/
        : return final_body : final daemon documentation body including the docstrings
        """        
        # if the text points us to the raw daemon code
        if config.DAEMON_DOC_ARGS_REGEX.search(body) is not None:
            for match in config.DAEMON_DOC_ARGS_REGEX.finditer(body):
                daemon_filename = match.group(1)
                daemon_func = match.group(2)
                daemon_prog = match.group(3)
                start_idx = match.start()
                end_idx = match.end()
            # construct the download url for the raw body of each daemon
            daemon_code_url = self.root_download_url+f'/{daemon_filename}'
            daemon_code  = requests.get(daemon_code_url).content.decode("utf-8") 
            # try to match the 2 other regexes that extract the docstring
            full_matches = ''
            if config.DAEMON_DESC_REGEX.search(daemon_code) is not None:
                for match in config.DAEMON_DESC_REGEX.finditer(daemon_code):
                    description_match = match.group(1)
                    description_match = description_match[1:-1]
                    full_matches = full_matches  + description_match
            if config.DAEMON_EPILOG_REGEX.search(daemon_code) is not None:
                for match in config.DAEMON_EPILOG_REGEX.finditer(daemon_code):
                    epilog_match = match.group(1)
                    full_matches = full_matches  + epilog_match
            # put the above in the correct place
            final_body = body[:start_idx] + full_matches + body[end_idx:]
            return final_body
        # else keep initial body of the daemon
        else:            
            return body


    def fetch(self, api_token):
        """
        Return a pandas DataFrames that hold information for 
        Rucio's documentation. Utilizes GitHub's api.

        :param api_token : GitHub api token used for fetching the data
        :return docs_df  : DataFrame containing all the information for Rucio's docs
        """        
        self.api_token = api_token
        self.headers = {'Content-Type': 'application/json', 'Authorization': f'token {self.api_token}'} 
        self._check_token()
        
        docs_df = pd.DataFrame(columns=['doc_id','name', 'file_type',
                                        'url','download_url','body', 'doc_type'])

        doc_id = 0
        print("Fetching...")
        for doc in tqdm(helpers.request(self.docs_url, self.headers)):
            if type(doc) == str:
                # if the api_token is not correct, we are going to get an error on every issue
                print(f"Error: Problem fetching the doc {doc} moving on to the next...")
                continue
            # handle files
            elif doc['type'] == 'file':
                doc_name         = doc['name']
                doc_file_type    = doc['type']
                doc_url          = doc['html_url']
                doc_download_url = doc['download_url']
                # not to be confused with 'request' function from helpers that returns json
                doc_body         = requests.get(doc_download_url).content.decode("utf-8") 
                docs_df = docs_df.append({
                    'doc_id' : doc_id,
                    'name': doc_name,
                    'file_type': doc_file_type,
                    'url': doc_url,
                    'download_url' : doc_download_url,
                    'body': doc_body,
                    'doc_type': 'general'
                    }, ignore_index=True)
                doc_id += 1 

            # handle directories 
            elif doc['type'] == 'dir':
                if doc['name'] == 'images':
                    # No need to fetch images in this version
                    pass

                # daemon documentation exists under the man directory
                elif doc['name'] == 'man':
                    print("\nFetching the daemon documentation...")
                    man_url = doc['url']
                    # in order to avoid an extra loop we hardcoded the daemons doc link for rucio
                    try:
                        daemons_url = self.root_download_url+'/doc/source/man/daemons.rst'
                        daemon_body = requests.get(daemons_url).content.decode("utf-8")
                        # regex used to extract daemon names from body
                        daemons = re.findall('rucio-.*$', daemon_body, re.MULTILINE)
                    except:
                        raise AssertionError('There is a problem with the daemons_url. Double check if it has changed')
                    for man_doc in helpers.request(man_url, self.headers):
                        if type(man_doc) == str:
                            print(f"Error : There was a problem fetching the file : {man_doc}")
                            continue
                        else:
                            # make sure that we are looking at daemon documentation, by utilize daemon names gathered above
                            if man_doc['name'].split('.')[0] in daemons:
                                doc_name         = man_doc['name']
                                doc_file_type    = man_doc['type']
                                doc_url          = man_doc['html_url']
                                doc_download_url = man_doc['download_url']
                                # In Rucio daemons the doc_body usually points to the docsting documentation 
                                doc_body         = requests.get(doc_download_url).content.decode("utf-8")
                                # We need additional handling to get it, done with _extract_daemon_body method
                                final_doc_body   = self._extract_daemon_body(doc_body)                                
                                docs_df = docs_df.append({
                                            'doc_id' : doc_id,
                                            'name': doc_name,
                                            'file_type': doc_file_type,
                                            'url': doc_url,
                                            'download_url' : doc_download_url,
                                            'body': final_doc_body,
                                            'doc_type': 'daemon'
                                            }, ignore_index=True)
                                doc_id += 1       
                    
                # handle the release notes
                elif doc['name'] == 'releasenotes':
                    print("\nFetching the release notes...")
                    release_notes_url = doc['url']
                    for release_note in helpers.request(release_notes_url, self.headers):
                        if type(release_note) == str:
                            print(f"Error: Problem fetching the release note {release_note}")
                            continue
                        else:
                            doc_name         = release_note['name']
                            doc_file_type    = release_note['type']
                            doc_url          = release_note['html_url']
                            doc_download_url = release_note['download_url']
                            doc_body         = requests.get(doc_download_url).content.decode("utf-8") 
                            docs_df = docs_df.append({
                                        'doc_id' : doc_id,
                                        'name': doc_name,
                                        'file_type': doc_file_type,
                                        'url': doc_url,
                                        'download_url' : doc_download_url,
                                        'body': doc_body,
                                        'doc_type': 'release_notes'
                                        }, ignore_index=True)
                            doc_id += 1    
                        
                # handling restapi documentation
                elif doc['name'] == 'restapi':
                    # this is a bit complicated for now, if we want to integrate there is a need to 
                    # download and compile with Sphinx and the Makefile etc
                    pass
                # handling api documentation
                elif doc['name'] == 'api':
                    # this is a bit complicated for now, if we want to integrate there is a need to 
                    # download and compile with Sphinx and the Makefile etc
                    pass
        self.docs = docs_df    
        return docs_df


    def save(self, db = Database, docs_table_name = 'docs'):
        """
        Save the data in a .db file utilizing the bot.database.py sqlite wrapper

        : param db                 : bot.database Database object 
        : param  docs_table_name   : name of the table where we'll store the docs
        """
        if hasattr(self, 'docs'):
            print('Saving...')
            self.docs.to_sql(docs_table_name, con=db.db, if_exists='replace', index=False)
        else:
            raise SavingError(f"\nError: We are missing the data. Please use the .fetch() method before saving.")


    def load(self, db = Database, docs_table_name = 'docs'):
        """
        Load the data from the .db file.

        : param  db                  : bot.database Database object 
        : param  docs_table_name     : name of the table where we'll store the docs
        : return docs                : DataFrame holding the documentation data
        """
        try:
            print('Loading...')
            self.docs = db.get_dataframe(f'{docs_table_name}')
            return self.docs
        except:
            raise LoadingError(f"\nError: Data not found.")            
            


class LoadingError(Exception):
    """Raised when the data we are trying to load isn't found."""
    pass

class SavingError(Exception):
    """Raised when the dataframe(s) we are trying to save are missing."""
    pass

class InvalidRepoError(Exception):
    """Raised when the repository for the IssueFetcher is not correct."""
    pass

class InvalidTokenError(Exception):
    """Raised when the OAUTH token for the GitHub api is not correct."""
    pass

################################################################################################################################################
if __name__ == "__main__":
    # example of loading issues data
    # data_storage = Database('dataset.db')
    # print("Let's create an IssuesFetcher")
    # fetcher = FetcherFactory.get_fetcher('Issue')
    # issues_df, comments_df = fetcher.load(db=data_storage, issues_table_name='issues', comments_table_name='issue_comments')
    # print(issues_df.head())
    # print(comments_df.head())    

    
    # example of loading documentation data 
    # data_storage = Database('dataset.db')
    # print("Let's create a RucioDocsFetcher")
    # fetcher = FetcherFactory.get_fetcher('Rucio Documentation')
    # docs_df = fetcher.load(db=data_storage, docs_table_name='docs')
    # print(docs_df.info())
