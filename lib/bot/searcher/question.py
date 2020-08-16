# bot modules
from bot.searcher.base import SearchEngine
from bot.database.sqlite import Database
# general python
import pandas as pd

class QuestionSearchEngine(SearchEngine):
    """Question Search Engine"""

    def __init__(self, doc_id='question_id', index=['question']):
        """
        Creates the Question Search Engine.

        This search engine is used to match user questions with
        the most similar previously asked questions.

        <!> Note : A question search engine assumes that the original_table 
        we are indexing is the result of the QuestionDetector.
        Which means the context of each question is known.

        :param doc_id : id of the document we are indexing (default is question_id)
        :param index  : Name of column(s) that will be indexed. (default is ['question']) 
        :type index   : list
        """
        super().__init__(index=index,ids=doc_id)
        self.type = 'Question Search Engine'

    def _attach_qa_data(self, results, query):
        """
        Attach the columns needed to transform the results
        DataFrame into SQuAD like data. 

        For Question documents (in QuestionSearchEngine) 
        the question and context columns already exist and hold
        stored data, only user_query is added.
        """ 
        results["user_query"] = query
    
    def create_index(self, corpus=pd.DataFrame, db=Database, table_name='question_doc_term_matrix'):
        super().create_index(corpus=corpus, db=db, table_name=table_name)

    def load_index(self, db=Database, table_name='question_doc_term_matrix', original_table='questions'):
        super().load_index(db=db, table_name=table_name, original_table=original_table)

if __name__ == "__main__":

    data_storage = Database('data_storage.db', 'questions')
    print("Let's create a QuestionSearchEngine")
    qse = QuestionSearchEngine()
    
    # # how to save
    # # just for email questions
    q_df = data_storage.get_dataframe('questions')
    print(q_df.info())
    
    # save
    qse.create_index(corpus=q_df, db=data_storage)
    # how to load
    # qse.load_index(db=data_storage, table_name='documentation_doc_term_matrix', original_table='docs')


    question = 'Rucio-account?'
    
    results = qse.search(question, 10)
    print(f"\nQUESTION : {question}")

    print("\nGENERAL INFO OF WHAT WAS RETRIEVED:")
    print(results)
    
    # data_storage.close_connection()
    print(results.columns)
    
    print(results.index)

    for q in results.question.values:
        print(q)