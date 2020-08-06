# bot modules
from bot.database.sqlite import Database
from bot.parser.interface import IParser
# general python
import pandas as pd
from tqdm import tqdm

## Rucio Docs
class RucioDoc():
    """Rucio Documentation object"""
    def __init__(self, doc_id, name, url, body, doc_type):
        self.doc_id   = int(doc_id)
        self.name     = name 
        self.url      = url
        self.body     = body
        self.doc_type = doc_type 


class RucioDocsParser(IParser):
    def __init__(self):
        self.type = 'Rucio Documentation Parser'

    def parse(self, doc_id, name, url, body, doc_type, db=Database, docs_table_name='docs'):
        """
        Parses a single Rucio documentation file.

        <!> Note: For now we only check for the length of the file to decide if we are intrested in it.
        Once evaluation on the performance of the bot is done, additional prcessing and information
        extraction methods will be applied on the documentation as well as the rest of our input data

        :param [doc_id,...,doc_type]  : all the raw documentation attributes
        :param db                     : <bot Database object> to where we store the parsed docs
        :param docs_table_name        : in case we need use a different table name (default 'docs')
        :returns doc                  : an <RucioDoc object> created by the RucioDocsParser
        """
        doc = RucioDoc(doc_id    = doc_id, 
                       name      = name,
                       url       = url,
                       body      = body,
                       doc_type  = doc_type)

        # save documentation to db
        if len(doc.body) < 50: 
            return doc
        else:
            db.insert_doc(doc, table_name=docs_table_name)
        return doc

    def parse_dataframe(self, docs_df, db= Database, docs_table_name='docs', return_docs=False):
        """
        Parses the entire fetched documentation dataframe,
        creates <RucioDoc objects> and saves them to db.
        
        Expects a <pandas DataFrame object> as input that holds the raw fetched docs.
        For more information about the structure and content of docs_df look at the RucioDocsFetcher.

        :param docs_df     : <pandas DataFrame object> containing all documentation data
        :param db          : <bot Database object> to save the <RucioDoc objects>
        :param return_docs : True/False on if we return a list of <RucioDoc objects> (default False)
        :returns docs      : a list of <RucioDoc objects> created by the RucioDocsParser 
        """
        docs = []
        print("Parsing Rucio Documentation...")
        for i in tqdm(range(len(docs_df.index))):
            doc = self.parse(doc_id            = docs_df.doc_id.values[i],
                               name            = docs_df.name.values[i],
                               url             = docs_df.url.values[i],
                               body            = docs_df.body.values[i],
                               doc_type        = docs_df.doc_type.values[i],
                               db              = db,
                               docs_table_name = docs_table_name)
            if return_docs:
                docs.append(doc)
            else:
                continue
        return docs

