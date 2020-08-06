# bot modules
from bot.parser.comments import IssueCommentParser
from bot.parser.issues   import IssueParser
from bot.parser.docs     import RucioDocsParser
from bot.parser.emails   import EmailParser

class ParserFactory():
    @staticmethod
    def get_parser(data_type):
        """
        Select between 
        - Issue
        - Issue Comment
        - Rucio Documentation
        - Email

        :returns parser: a <Parser object> 
        """
        try:
            if data_type == 'Issue':
                return IssueParser()
            if data_type == 'Issue Comment':
                return IssueCommentParser()
            if data_type == 'Rucio Documentation':
                return RucioDocsParser()
            if data_type == 'Email':
                return EmailParser()
            raise AssertionError("Parser not found")
        except AssertionError as _e:
            print(_e)

if __name__ == "__main__":
    pass