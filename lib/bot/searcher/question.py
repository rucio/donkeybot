# bot modules
from bot.searcher.base import SearchEngine
from bot.database.sqlite import Database

# general python
import pandas as pd


class QuestionSearchEngine(SearchEngine):
    """Question Search Engine"""

    def __init__(self, ids="question_id", index=["question"]):
        """
        Creates the Question Search Engine.

        This search engine is used to match user questions with
        the most similar previously asked questions.

        <!> Note : A question search engine assumes that the original_table
        we are indexing is the result of the QuestionDetector.
        Which means the context of each question is known.

        :param ids    : id of the document we are indexing (default is question_id)
        :param index  : Name of column(s) that will be indexed. (default is ['question'])
        :type index   : list
        """
        super().__init__(index=index, ids=ids)
        self.type = "Question Search Engine"

    def _attach_qa_data(self, results, query):
        """
        Attach the columns needed to transform the results
        DataFrame into SQuAD like data.

        results include : {
                    'query'    : what the user queried in the SE
                    'context'   : context of user_query/question
                }

        For Question documents (in QuestionSearchEngine)
        "context" column already, only user's "query" is added.
        """
        results["query"] = query

    def create_index(
        self, corpus=pd.DataFrame, db=Database, table_name="question_doc_term_matrix"
    ):
        super().create_index(corpus=corpus, db=db, table_name=table_name)

    def load_index(
        self,
        db=Database,
        table_name="questions_doc_term_matrix",
        original_table="questions",
    ):
        super().load_index(db=db, table_name=table_name, original_table=original_table)
