# bot modules
from bot.detector.question.base import Question, QuestionOriginNotSet
from bot.database.sqlite import Database

class CommentQuestion(Question):
    """Question originating from GitHub issue comments"""
    
    def __init__(self, question_text = None,
                start_idx = None,
                end_idx = None,
                question_id = None):
        super().__init__(question_text, start_idx, end_idx, question_id, 'comment')
        
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
        self.issue_id   = None
        self.comment_id = origin_id

    def find_context_from_table(self, db=Database, table_name='issue_comments'):
        """
        Depending on the question's origin, find the corresponding 
        context based on the appropriate table.
        
        - comments  : The context are the bodies of the comments under
                      the issue and after the comment where the question
                      was asked

        <!> Note: The origin_id of the comment needs to have been set by 
        calling set_origin_id() before using this method.

        :param db         : <bot.database obj>
        :param table_name : name of the table where the context exists
        """
        if self.comment_id is not None:
            self.issue_id, self.date_question_was_asked = \
                        db.query(f'''SELECT issue_id, created_at
                                     FROM {table_name}
                                     WHERE comment_id == {self.comment_id}
                                     ''')[0] 
            result =  db.query(f'''SELECT clean_body
                                   FROM {table_name}
                                   WHERE comment_id IN (
                                       SELECT comment_id
                                       FROM {table_name}
                                       WHERE issue_id == "{self.issue_id}"
                                             and created_at   > "{self.date_question_was_asked}"
                                    )
                                    ORDER BY created_at ASC
                                ''')
            self.context = " ".join([res[0] for res in result])
        else:
            raise QuestionOriginNotSet(f"\nError: The comment_id for the Question object has not been set.Try using set_origin_id() method.")
