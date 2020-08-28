# bot modules
import bot.utils as utils
from bot.database.sqlite import Database
from bot.parser.interface import IParser

# general python
import pandas as pd
import re
from tqdm import tqdm


class Issue:
    """GitHub Issue"""

    def __init__(
        self, issue_id, title, state, creator, created_at, comments, body, clean_body
    ):
        self.issue_id = int(issue_id)
        self.title = title
        self.state = state
        self.creator = creator
        self.created_at = created_at
        self.comments = int(comments)
        self.body = body
        self.clean_body = clean_body


class IssueParser(IParser):
    """GitHub Issue Parser"""

    def __init__(self):
        self.type = "Issue Parser"

    def parse(
        self,
        issue_id,
        title,
        state,
        creator,
        created_at,
        comments,
        body,
        db=Database,
        issues_table_name="issues",
    ):
        """
        Parses a single issue.
        
        <!> Note  : The parse() method is only expected to be used after an an issues table
        has been created in the db. To create said table use the Database object's 
        .create_issues_table() method before attempting to parse.
        
        :param [issue_id,...,body]  : all the raw issue attributes
        :param db                 : <bot Database object> to where we store the parsed issues
        :param issues_table_name  : in case we need use a different table name (default 'issues')
        :returns issue            : an <Issue object> created by the IssueParser
        """
        # The date format returned from the GitHub API is in the ISO 8601 format: "%Y-%m-%dT%H:%M:%SZ"
        issue_created_at = utils.convert_to_utc(created_at, "%Y-%m-%dT%H:%M:%SZ")
        issue_clean_body = utils.pre_process_text(
            self.clean_issue_body(body), fix_url=True
        )
        issue = Issue(
            issue_id=issue_id,
            title=title,
            state=state,
            creator=creator,
            created_at=issue_created_at,
            comments=comments,
            body=body,
            clean_body=issue_clean_body,
        )

        # no comments -> no context,  only insert relevant data to db
        if issue.comments > 0:
            db.insert_issue(issue, table_name=issues_table_name)
        return issue

    def parse_dataframe(
        self,
        issues_df=pd.DataFrame,
        db=Database,
        issues_table_name="issues",
        return_issues=False,
    ):
        """
        Parses the entire fetched issues dataframe, creates <Issue objects> and saves them to db.
        
        Expects a <pandas DataFrame object> as input that holds the raw fetched issues.
        For more information about the structure and content of issues_df look at the IssueFetcher.

        :param issues_df     : <pandas DataFrame object> containing all issues
        :param db            : <bot Database object> to save the <Issue objects>
        :param return_issues : True/False on if we return a list of <Issue objects> (default False)
        :returns issues      : a list of <Issue objects> created by the IssueParser 
        """
        issues = []
        print("Parsing issues...")
        for i in tqdm(range(len(issues_df.index))):
            issue = self.parse(
                issue_id=issues_df.issue_id.values[i],
                title=issues_df.title.values[i],
                state=issues_df.state.values[i],
                creator=issues_df.creator.values[i],
                created_at=issues_df.created_at.values[i],
                comments=issues_df.comments.values[i],
                body=issues_df.body.values[i],
                db=db,
                issues_table_name=issues_table_name,
            )
            if return_issues:
                issues.append(issue)
            else:
                continue
        return issues

    @staticmethod
    def clean_issue_body(body):
        """ 
        Cleans up the body of an issue from 
        ISSUE_TEMPLATE patterns in Rucio.

        :returns clean_body : cleaned issue body
        """
        clean_body = (
            body.strip("\n\r")
            .replace("Motivation", "")
            .replace("Modification", "")
            .replace("Expected behavior", "")
            .replace("\n", " ")
            .replace("\r", " ")
            .replace("-", " ")
            .strip()
        )
        clean_body = re.sub(" +", " ", clean_body).strip(" ")
        return clean_body
