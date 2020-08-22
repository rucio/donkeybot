# bot modules
from bot.searcher.base import SearchEngine
from bot.database.sqlite import Database

# general python
import pandas as pd


class FAQSearchEngine(SearchEngine):
    """FAQ Search Engine"""

    def __init__(self, ids="faq_id", index=["keywords", "question"]):
        """
        Creates the FAQ Search Engine.

        This search engine is used to match user questions with
        the most similar FAQ question.

        :param ids    : id of the document we are indexing (default is faq_id)
        :param index  : Name of column(s) that will be indexed. (default is ["keywords", "question"]) 
        :type index   : list
        """
        super().__init__(index=index, ids=ids)
        self.type = "FAQ Search Engine"

    def _attach_qa_data(self, results, query):
        """
        Attach the columns needed to transform the results
        DataFrame into SQuAD like data. 

        results include : {
                    'query'    : what the user queried in the SE
                    'context'  : context of user_query/question
                }

        For FAQ documents "context" is basically the "answer" table
        from the retrieved question.
        """
        results["query"] = query
        results["context"] = answer 

    def create_index(
        self, corpus=pd.DataFrame, db=Database, table_name="faq_doc_term_matrix"
    ):
        super().create_index(corpus=corpus, db=db, table_name=table_name)

    def load_index(
        self,
        db=Database,
        table_name="faq_doc_term_matrix",
        original_table="faq",
    ):
        super().load_index(db=db, table_name=table_name, original_table=original_table)
