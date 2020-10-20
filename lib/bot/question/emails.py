# bot modules
from bot.question.base import Question, QuestionOriginNotSet
from bot.database.sqlite import Database


class EmailQuestion(Question):
    """Question originating from emails"""

    def __init__(
        self, question_text=None, start_idx=None, end_idx=None, question_id=None
    ):
        super().__init__(question_text, start_idx, end_idx, question_id, "email")

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
        self.email_id = origin_id
        self.issue_id = None
        self.comment_id = None

    def find_context_from_table(self, db=Database, table_name="emails"):
        """
        Depending on the question's origin, find the corresponding
        context based on the appropriate table.

        - emails    : The context are the bodies of the reply emails
                      in the same conversation, after the email where
                      the question was asked.

        <!> Note: The origin_id of the email needs to have been set by
        calling set_origin_id() before using this method.

        :param db         : <bot.database obj>
        :param table_name : name of the table where the context exists

        """
        if self.email_id is not None:
            (
                self.clean_body,
                self.conversation_id,
                self.date_question_was_asked,
            ) = db.query(
                f"""SELECT clean_body, conversation_id, email_date
                                  FROM {table_name}
                                  WHERE email_id == {self.email_id}
                                  """
            )[
                0
            ]
            if self.conversation_id is None:
                self.context = None
            else:
                result = db.query(
                    f"""SELECT clean_body
                                       FROM {table_name}
                                       WHERE email_id IN (
                                           SELECT email_id
                                           FROM {table_name}
                                           WHERE conversation_id == "{self.conversation_id}"
                                                 and email_date   > "{self.date_question_was_asked}"
                                        )
                                        ORDER BY email_date ASC
                                        """
                )
                self.context = " ".join([res[0] for res in result])
        else:
            raise QuestionOriginNotSet(
                f"\nError: The email_id for the Question object has not been set.Try using set_origin_id() method."
            )
