# bot modules
from bot.database.sqlite import Database

# general python
from abc import abstractmethod, ABC

# general python
from uuid import uuid4


class Question(ABC):
    def __init__(
        self,
        question_text=None,
        start_idx=None,
        end_idx=None,
        question_id=None,
        origin="other",
    ):
        """
        Question constructor.

        :param origin : 'email','question','comment' or 'other'
        """
        # Set unique ID or given from user input
        if question_id:
            self.id = str(question_id)
        else:
            self.id = str(uuid4().hex)
        self.question = question_text
        self.start = start_idx
        self.end = end_idx
        self.origin = origin
        self.context = None

    @abstractmethod
    def set_origin_id(self, origin_id):
        """ 
        Sets the origin id of a given question.

        Possible origins:
         - email_id
         - issue_id
         - comment_id

        <!> Note: Depending on the origin the id is set
        and the rest are left equal to None.

        :param origin_id : id of a given question's origin        
        """
        self.email_id = None
        self.issue_id = None
        self.comment_id = None

    @abstractmethod
    def find_context_from_table(self, db=Database, table_name=None):
        """
        Depending on the question's origin, find the corresponding 
        context based on the appropriate table.
        
        - emails    : The context are the bodies of the reply emails 
                      in the same conversation, after the email where 
                      the question was asked.
        - issues    : The context are the bodies of the comments under
                      the issue.
        - comments  : The context are the bodies of the comments under
                      the issue and after the comment where the question
                      was asked

        <!> Note: The origin_id needs to have been set by 
        calling set_origin_id() before using this method.

        :param db         : <bot.database obj>
        :param table_name : name of the table where the context exists
        """
        pass

    # user query comes, SE finds context, set_context is called.
    def set_context(self, text):
        """Used to set the context of a question object"""
        self.context = text

    def __str__(self):
        """String printed when calling the print function"""
        return f"id = {self.id}\nquestion_text = {self.question}\nstart = {self.start}\nend = {self.end}\norigin = {self.origin}"


class QuestionOriginNotSet(Exception):
    """Raised when the origin_id for the Question object has not been set"""

    pass
