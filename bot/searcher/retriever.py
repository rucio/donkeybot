# bot modules
import bot.utils as utils
from bot.database.sqlite import Database
# general python
from abc import ABCMeta, abstractmethod
import pandas as pd 
import numpy as np
from rank_bm25 import BM25Okapi
import string
import sys


class SearchEngine():
    
    def __init__(self, se_type):
        """
        The job of the SearchEngine is to retrieve the most similar
        question and/or documents from a created document term matrix (index)
        based on a provided user question/query.
                
        <!> Note: You have to create/load the index before using the 
                  SearchEngine

        if se_type == 'Question' then the SearchEngine
        expects to be used in question indexes where the 
        context has already been mined. Either from emails
        or issues.

        if se_type == 'Document' then the SearchEngine 
        expects to be used in general documentation text
        where the context will be the text that is retrieved.
        For example in Rucio's documentation.

        :param se_type: 'Documents' or 'Documents'
        """
        try:
            if se_type == 'Questions': 
                self.type = 'Question Search Engine'
                # column name for the id given to questions from QuestionDetector
                self.document_ids_name = 'question_id'
                self.column_to_index = 'question'
                return
            elif se_type == 'Documentation':
                self.type = 'Documentation Search Engine'
                # column name for the id given to documentation from the Fetcher/Parser
                self.document_ids_name = 'doc_id'
                # I think doc_type is also usefull to exist in the text that we index
                # since it describes the documentation type. For now at least until options
                # for specific keyword searching are added (eg. search on doc_type == 'release_notes')
                self.column_to_index = ['doc_type', 'body']
                return
            raise AssertionError("Error : Search Engine can only be of type 'Documents' or 'Documents'.")
        except AssertionError as _e:
            print(_e)
        return
        

    def search(self, question, top_n):
        """
        Return at most the `top_n` results most similar to
        the input `question` based on BM25.

        <!> Note : If some of the results don't pass all of our checks
                   then said result isn't  returned. Thus, the number of 
                   returned results are always <= top_n.

                   eg. If a Question has no Context we don't need it for our
                       next step so it's discarded
                
        :param top_n    : the maximum number of results that are returned
        :param question : User's question/query 
        :type top_n     : Integer
        :return results : pd.DataFrame object of the results 
        """
        try:
            if hasattr(self, 'index'):
                search_terms = utils.preprocess(question)
                doc_scores = self.bm25.get_scores(search_terms)  
                # sort results
                ind = np.argsort(doc_scores)[::-1][:top_n]  
                # results df
                results = self.corpus.iloc[ind][self.columns]  
                results["bm25_score"] = doc_scores[ind] 
                # here we can add any additional metadata we please
                results = results[results.bm25_score > 0]

                # any rules for the retrieved questions/documents
                if self.type == 'Question Search Engine':
                    # if there is no context don't return it
                    results = results[results.context != ""]
                elif self.type == 'Documentation Search Engine':
                    pass

                return results.reset_index()
            else:
                raise MissingDocumentTermMatrixError(f"\nError: The document term matrix was not found. Please create it using the create_index() method,\
                     or load it from memory with the load_index() method.")
        except MissingDocumentTermMatrixError as _e:
            sys.exit(_e)


    def create_index(self, corpus = pd.DataFrame, db = Database, table_name = 'doc_term_matrix'):
        """
        Takes a pandas DataFrame as input and create the SearchEngine's index.

        : param corpus     : pandas DataFrame object 
        : param db         : <bot.database.sqlite Database object> where the index will be stored
        : param table_name : Name of the doc term matrix table to be saved on the db ( default = doc_term_matrix) 
        """
        self.corpus  = corpus
        self.columns = self.corpus.columns

        if self.type == 'Question Search Engine':
            documents = self.corpus[self.column_to_index].fillna("")
        elif self.type == 'Documentation Search Engine':
            documents = (
                # documentation type [0] + documentation body [1]
                self.corpus[self.column_to_index[0]].fillna("") + " " + self.corpus[self.column_to_index[1]].fillna("") 
            )

        self.index   = documents.apply(utils.preprocess).to_frame()
        self.index.columns = ["terms"]
        # on the QuestionSearchEngine the question_id is the index's index
        self.index.index = self.corpus[self.document_ids_name]
        self.bm25 = BM25Okapi(self.index.terms.tolist())

        # turn terms from list to comma seperated values so we can save it into db
        self.index.terms = self.index.terms.apply(lambda x: ", ".join(x))
        # save to db
        self.index.to_sql(table_name, con=db.db, if_exists='replace', index=True)


    def load_index(self, db = Database, table_name = 'doc_term_matrix'):
        """
        Takes a <bot.database.sqlite Database object> as input and loads
        the SearchEngine's index and corpus.

        : param db      : <bot.database.sqlite Database object> where the index will be stored
        """
        try:
            # self.corpus  = db.get_dataframe(f'docs')
            # self.corpus  = db.get_dataframe(f'{table_name}')

            if self.type == 'Question Search Engine':
                # load the doc term matrix for just the question
                self.corpus  = db.get_dataframe('questions')
                self.columns = self.corpus.columns
                # documents = self.corpus[self.column_to_index].fillna("")
            elif self.type == 'Documentation Search Engine':
                self.corpus  = db.get_dataframe('docs')
                self.columns = self.corpus.columns
                # load the doc term matrix for documentation type + documentation body
                # documents = (
                #     self.corpus[self.column_to_index[1]].fillna("") + " " + self.corpus[self.column_to_index[0]].fillna("") 
                # )
            # make sure the index is for the correct document ( here question_id )
            self.index = db.get_dataframe(f'{table_name}').set_index(self.document_ids_name, drop=True)
            # print(f"HERE P{self.index}")
            # turn comma seperated values back into lists in the dataframe
            self.index.terms = self.index.terms.apply(lambda x: x.split(", "))
            self.bm25 = BM25Okapi(self.index.terms.tolist())
        except Exception as _e:
            print(_e)


class MissingDocumentTermMatrixError(Exception):
    """Raised when we have missing attributes for our SearchEngine"""
    pass



############################################################################################
if __name__ == "__main__":

    data_storage = Database('data_storage.db', 'docs')
    print("Let's create a DocumentationSearchEngine")
    docs_qse = SearchEngine('Documentation')
    
    # # how to save
    # # just for email questions
    docs_df = data_storage.get_dataframe('docs')
    docs_qse.create_index(corpus=docs_df, db=data_storage, table_name='documentation_doc_term_matrix')

    # how to load
    # docs_qse.load_index(db=data_storage, table_name='documentation_doc_term_matrix')
    question = 'I want to delete a dataset replica'
    print(f"\nQUESTION : {question}")
    # print("\nMOST SIMILAR QUESTIONS FROM PREVIOUS EMAILS : ")
    # print(docs_qse.search(question, 2)['question'].values)
    print("\nMOST SIMILAR DOCUMENTATION: ")
    print(docs_qse.search(question, 2)['name'].values)
    print("\nCONTEXT : ")
    print(docs_qse.search(question, 2)['body'].values)
    # print("\nTHEIR ID : ")
    # print(docs_qse.search(question, 2)['question_id'].values)

    print("\nGENERAL INFO OF WHAT WAS RETRIEVED:")
    print(docs_qse.search(question, 2).head())

    data_storage.close_connection()
    