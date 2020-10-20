# bot modules
import bot.utils as utils
from bot.database.sqlite import Database
from bot.parser.interface import IParser

# general python
import pandas as pd
from tqdm import tqdm


class IssueComment:
    """GitHub Issue's Comment"""

    def __init__(self, issue_id, comment_id, creator, created_at, body, clean_body):
        self.issue_id = int(issue_id)
        self.comment_id = int(comment_id)
        self.creator = creator
        self.created_at = created_at
        self.body = body
        self.clean_body = clean_body


class IssueCommentParser(IParser):
    """GitHub Issue Comment Parser"""

    def __init__(self):
        self.type = "Issue Comment Parser"

    def parse(
        self,
        issue_id,
        comment_id,
        creator,
        created_at,
        body,
        db=Database,
        issue_comments_table="issue_comments",
    ):
        """
        Parses a single issue's comment.

        :param [issue_id,...,body]   : all the raw issue comment's attributes
        :param db                    : <bot Database object> to where we store the parsed issue comments
        :param issue_comments_table  : in case we need use a different table name (default 'issue_comments')
        :returns issue_comment       : IssueComment object
        """
        # The date format returned from the GitHub API is in the ISO 8601 format: "%Y-%m-%dT%H:%M:%SZ"
        issue_comment_created_at = utils.convert_to_utc(
            created_at, "%Y-%m-%dT%H:%M:%SZ"
        )
        issue_comment_clean_body = utils.pre_process_text(
            body, fix_url=True, remove_newline=True
        )
        issue_comment = IssueComment(
            issue_id=issue_id,
            comment_id=comment_id,
            creator=creator,
            created_at=issue_comment_created_at,
            body=body,
            clean_body=issue_comment_clean_body,
        )

        db.insert_issue_comment(issue_comment, table_name=issue_comments_table)
        return issue_comment

    def parse_dataframe(
        self,
        comments_df=pd.DataFrame,
        db=Database,
        issue_comments_table="issue_comments",
        return_comments=False,
    ):
        """
        Parses the entire fetched issue comments dataframe, creates IssueComment objects and saves them to db.

        For more information about the structure and content of comments_df look at the IssueFetcher.

        :param comments_df       : pandas DataFrame object containing all issue comments
        :param db                : bot Database object to save the IssueComment objects
        :param return_comments   : Boolean -> if we return a list of IssueComment objects (default False)
        :returns issue_comments  : list of IssueComment objects
        """
        issue_comments = []
        print("Parsing issue comments...")
        for i in tqdm(range(len(comments_df.index))):
            issue_comment = self.parse(
                issue_id=comments_df.issue_id.values[i],
                comment_id=comments_df.comment_id.values[i],
                creator=comments_df.creator.values[i],
                created_at=comments_df.created_at.values[i],
                body=comments_df.body.values[i],
                db=db,
                issue_comments_table=issue_comments_table,
            )
            if return_comments:
                issue_comments.append(issue_comment)
            else:
                continue
        return issue_comments
