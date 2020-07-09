# bot modules
import bot.helpers as helpers
from bot.database import Database
# general python
from abc import ABCMeta, abstractmethod
import pandas as pd 
import numpy as np
from rank_bm25 import BM25Okapi
import string


class ISearchEngine(metaclass=ABCMeta):
    """The Search Engine Interface"""
    
    @abstractmethod
    def search():
        """Returns results from index that match the query"""
        pass

    @abstractmethod
    def create_index():
        """Create the Search Engine's index"""
        pass

    @abstractmethod
    def load_index():
        """Load the Search Engine's index"""
        pass


class SearchEngineFactory():

    @staticmethod
    def get_engine(search_engine_type):
        try:
            if search_engine_type == 'Question':
                return QuestionSearchEngine()
            raise AssertionError("SearchEngine not found")
        except AssertionError as _e:
            print(_e)

class QuestionSearchEngine(ISearchEngine):
    
    def __init__(self):
        """
        You have to create/load the index before using the 
        SearchEngine
        """
        pass
        

    def search(self, question, top_n):
        """
        Return `top_n` questions that are the most similar to
        the input `question` based on BM25.

        <!> Note : If some of the results don't pass all of our checks
                   then said result isn't  returned. Thus, the number of 
                   returned results are always <= top_n.

                   eg. If a Question has no Context we don't need it for our
                       next step
                
        :param top_n    : the maximum number of results that are returned
        :type question  : String
        :type top_n     : Integer
        :return results : pd.DataFrame object with results 
                          and any metadata we want
        """
        if hasattr(self, 'index'):
            search_terms = helpers.preprocess(question)
            doc_scores = self.bm25.get_scores(search_terms)  
            # sort results
            ind = np.argsort(doc_scores)[::-1][:top_n]  
            # results df
            results = self.corpus.iloc[ind][self.columns]  
            results["bm25_score"] = doc_scores[ind] 
            # here we can add any additional metadata we please
            results = results[results.bm25_score > 0]
            # if there is no context don't return it
            results = results[results.context != ""]

            return results.reset_index()
        else:
            raise SearchEngineAttributesNotSet(f"\nError: The SearchEngine attributes have not been set. Please call the create_index or load_index methods before using the SearchEngine.")


    def create_index(self, corpus = pd.DataFrame, db = Database, index_table_name = 'questions_index'):
        """
        Takes a pandas DataFrame as input and create the SearchEngine's index.

        : param corpus           : pandas DataFrame object 
        : param db               : <bot.database Database object> where the index will be stored
        : param index_table_name : Optional and defaults to questions_index for this SearchEngine
        """
        self.corpus = corpus
        self.columns = self.corpus.columns
        documents = (
            self.corpus.question.fillna("")
        )
        self.index = documents.apply(helpers.preprocess).to_frame()
        self.index.columns = ["terms"]
        # on the QuestionSearchEngine the question_id is the indexe's index
        self.index.index = self.corpus.question_id
        self.bm25 = BM25Okapi(self.index.terms.tolist())

        # turn terms from list to comma seperated values so we can save it into db
        self.index.terms = self.index.terms.apply(lambda x: ", ".join(x))
        # save to db
        self.index.to_sql(index_table_name, con=db.db, if_exists='replace', index=True)


    def load_index(self, db = Database):
        """
        Takes a <bot.database Database object> as input and loads
        the SearchEngine's index and corpus.

        : param db      : <bot.database Database object> where the index will be stored
        """
        try:
            self.corpus = db.get_dataframe('questions')
            self.columns = self.corpus.columns
            documents = (
                self.corpus.question.fillna("")
            )
            # make sure the index is for the correct document ( here question_id )
            self.index = db.get_dataframe('questions_index').set_index('question_id',drop=True)
            # turn comma seperated values back into lists in the dataframe
            self.index.terms = self.index.terms.apply(lambda x: x.split(", "))
            self.bm25 = BM25Okapi(self.index.terms.tolist())
        except Exception as _e:
            print(_e)


class SearchEngineAttributesNotSet(Exception):
    """Raised when the attributes of the SearchEngine have not been set"""
    pass



############################################################################################
if __name__ == "__main__":
    data_storage = Database('dataset.db', 'questions')
    print("Let's create a QuestionSearchEngine")
    qse = SearchEngineFactory.get_engine('Question')
    qse.load_index(data_storage)
    question = 'i want to delete a replica'
    print(f"QUESTION : {question}")
    print("MOST SIMILAR QUESTIONS : ")
    print(qse.search(question, 2)['question'].values)
    print("THEIR CONTEXT : ")
    print(qse.search(question, 2)['context'].values)
    print("THEIR ID : ")
    print(qse.search(question, 2)['question_id'].values)

    data_storage.close_connection()
    