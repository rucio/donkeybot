# bot modules
import bot.utils as utils
from bot.database.sqlite import Database

# general python
import pandas as pd
import numpy as np
from rank_bm25 import BM25Okapi
import string
import sys


class SearchEngine:
    """Search Engine for Documents"""

    def __init__(self, index=["doc_type", "body"], ids="doc_id"):
        """
        The job of the SearchEngine is to retrieve the most similar
        document from the created document-term matrix (index).
                
        <!> Note: You have to create/load the index before using the 
                  .search() method.

        :param index : Name of column(s) that will be indexed. (default is ['doc_type', 'body'])
        :param ids   : id of the document we are indexing (default is doc_id)
        :type index  : list
        """
        self.type = "Document Search Engine"
        self.document_ids_name = ids
        # I think doc_type is also usefull to exist in the text that we index
        # since it describes the documentation type. For now at least until options
        # for specific keyword searching are added (eg. search on doc_type == 'release_notes')
        # recommended to migrate to Elasticsearch after prototype works sufficiently
        if type(index) == str:
            self.column_to_index = index.split()
        else:
            self.column_to_index = index

    def search(self, query, top_n):
        """
        Return at most the `top_n` results most similar to
        the input `query` based on BM25.
           
        :param top_n    : the maximum number of results that are returned
        :type top_n     : int
        :param query    : User's question/query 
        :return results : pd.DataFrame object of the results 
        """
        try:
            if hasattr(self, "index"):
                search_terms = self.preprocess(query)
                doc_scores = self.bm25.get_scores(search_terms)
                # sort results
                ind = np.argsort(doc_scores)[::-1][:top_n]
                # results dataframe
                results = self.corpus.iloc[ind][self.columns]
                results["bm25_score"] = doc_scores[ind]
                self._attach_qa_data(results, query)
                results = results[results.bm25_score > 0]
                return results.reset_index(drop=True)
            else:
                raise MissingDocumentTermMatrixError(
                    f"\nError: The document term matrix was not found. Please create \
                                                        it using the create_index() method,\
                                                        or load it from memory with the load_index() method."
                )
        except MissingDocumentTermMatrixError as _e:
            sys.exit(_e)

    def _attach_qa_data(self, results, query):
        """
        Attach the columns needed to transform the results
        DataFrame into SQuAD like data. 

        results include : {
             'user_query': what the user queried in the SE
             'question'  : the most similar question matched
             'context'   : context of user_query/question
        }

        For regular documents user_query and question are 
        the same (not a QuestionSearchEngine) and the columns 
        we have previously indexed are the context.
        """
        results["query"] = query
        results["question"] = query
        results["context"] = self._get_documents().to_frame()

    def _get_documents(self):
        """
        Concatenates the columns we want to index together and returns the
        resulting document.

        :returns documents : rows of concatenated string columns that will be
                             indexed. 
        :type documents    : pandas.core.series.Series object
        """
        try:
            documents = self.corpus[self.column_to_index].agg(" ".join, axis=1)
            return documents
        except Exception as _e:
            sys.exit(_e)

    def preprocess(self, text):
        """
        Preprocesses/prepares text for the Search Engine.
        """
        words = utils.pre_process_text(
            text,
            lower_text=True,
            remove_numbers=True,
            numbers_replacement=" ",
            remove_punctuation=True,
            punctuation_replacement=" ",
            remove_stop_words=True,
            stem=True,
            tokenize_text=True,
        )
        return list(set([word for word in words if len(word) > 2]))

    def create_index(
        self, corpus=pd.DataFrame, db=Database, table_name="doc_term_matrix"
    ):
        """
        Takes a pandas DataFrame as input and create the SearchEngine's document-term matrix(index).

        : param corpus     : pandas DataFrame object 
        : param db         : <bot.database.sqlite Database object> where the index will be stored
        : param table_name : Name of the doc term matrix table to be saved on the db ( default = doc_term_matrix) 
        """
        self.corpus = corpus
        self.columns = self.corpus.columns
        documents = self._get_documents()
        # create doc-term matrix
        self.index = documents.apply(lambda x: self.preprocess(x)).to_frame()
        self.index.columns = ["terms"]
        self.index.index = self.corpus[self.document_ids_name]
        self.bm25 = BM25Okapi(self.index.terms.tolist())
        self.index.terms = self.index.terms.apply(lambda x: ", ".join(x))
        # save to db
        self.index.to_sql(table_name, con=db.db, if_exists="replace", index=True)

    def load_index(
        self, db=Database, table_name="rucio_doc_term_matrix", original_table="docs"
    ):
        """
        Loads the document-term matrix and the original table we indexed to prepare
        the Search Engine for use.
    
        :param table_name     : document term matrix table name
        :param original_table : original table we indexed
        :param db             : <bot.database.sqlite Database object> where the index will be stored
        """
        try:
            self.corpus = db.get_dataframe(original_table)
            # let's not index the release-notes in this version of the bot
            # this code also exists in the create_se_indexes script for rucio documents
            if (
                self.type == "Document Search Engine"
            ):  # for us this is rucio documentation
                self.corpus = self.corpus[self.corpus["doc_type"] != "release_notes"]
            self.columns = self.corpus.columns
            self.index = db.get_dataframe(f"{table_name}").set_index(
                self.document_ids_name, drop=True
            )
            self.index.terms = self.index.terms.apply(lambda x: x.split(", "))
            self.bm25 = BM25Okapi(self.index.terms.tolist())
        except Exception as _e:
            print(_e)


class MissingDocumentTermMatrixError(Exception):
    """Raised when we have missing attributes for our SearchEngine"""

    pass
