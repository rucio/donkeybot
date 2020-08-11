# bot modules
from bot.detector.question.base import Question, QuestionOriginNotSet
from bot.database.sqlite import Database
# general python
from uuid import uuid4

class IssueQuestion(Question):
    """Question originating from GitHube issues"""
    
    def __init__(self, question_text = None,
                start_idx = None,
                end_idx = None,
                question_id = None):
        # Set unique ID or given from user input
        if question_id:
            self.id    = str(question_id)
        else:
            self.id    = str(uuid4().hex)
        self.question  = question_text
        self.start     = start_idx
        self.end       = end_idx
        self.context   = None 
        self.origin    = 'issue'
        

    def set_origin_id(self, origin_id):
        """ 
        Sets the origin id of a given question.
        
        Possible origins:
         - email_id
         - issue_id
         - comment_id

        <!> Note: Ids from different origin left None.

        :param origin_id : id of a given question's origin        
        """ 
        self.email_id   = None
        self.issue_id   = origin_id
        self.comment_id = None


    def find_context_from_table(self, db=Database, table_name='issues'):
        """
        Depending on the question's origin, find the corresponding 
        context based on the appropriate table.
        
        - issues    : The context are the bodies of the comments under
                      the issue.

        <!> Note: The origin_id of the issue needs to have been set by 
        calling set_origin_id() before using this method.

        :param db         : <bot.database obj>
        :param table_name : name of the table where the context exists
        """
        if self.issue_id is not None:
            self.clean_body, self.num_comments = \
                        db.query(f'''SELECT clean_body, comments
                                     FROM {table_name}
                                     WHERE issue_id == {self.issue_id}''')[0] 
            assert self.num_comments != 0
            result =  db.query(f'''SELECT clean_body
                                   FROM issue_comments
                                   WHERE issue_id  == "{self.issue_id}"
                                   ORDER BY created_at ASC
                                ''')
            self.context = " ".join([res[0] for res in result])
        else:
            raise QuestionOriginNotSet(f"\nError: The issue_id for the Question object has not been set.Try using set_origin_id() method.")
