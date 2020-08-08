# bot modules
import bot.config as config
# general python
import sqlite3
from sqlite3 import Error
import os.path
import pandas as pd


class Database:
    """Database wrapper for sqlite3"""

    def __init__(self, db_name, default_table='emails'):
        self.db_name = db_name
        try:
            self.db = sqlite3.connect(config.DATA_DIR + db_name)
        except Error as err:
            print(err)
        self.default_table = default_table
        self.cursor = self.db.cursor()
    

    def get_dataframe(self, table):
        """Return a pandas DataFrame object of the Database contents"""
        return pd.read_sql_query(f"SELECT * FROM {table}", self.db)


    def close_connection(self):
        """Close Database connection"""
        self.db.close()


    def drop_table(self, table):
        """Drop a table if it exists"""
        self.db.execute(f"DROP TABLE IF EXISTS {table}")


    def create_table(self, table_name, columns):
        """
        Create a new table.
        
        :param table_name   : the name we want to give
        :param columns      : a dictionary in the form of
                             {'col_name' : 'datatype'}
        """
        self.cols = ""
        for col_name, col_type in columns.items():
            self.cols += col_name+" "+col_type+","
        self.cols = self.cols[0:len(self.cols)-1]
        self.db.execute("CREATE TABLE IF NOT EXISTS {}({})".format(table_name,self.cols))
    

    def get_tables(self):
        """Return a list of tables in database"""
        self.tables = self.db.execute("SELECT name FROM sqlite_master")
        return list(self.tables)


    def query(self, query_string):
        """Run queries on the database"""
        self.cursor.execute(query_string)
        return self.cursor.fetchall()

    # emails
    def create_emails_table(self, table_name='emails'):
        """
        Creates a table to store Email objects from EmailParser.
        Knows about their attributes and creates the corresponding columns.

        :param table_name : name given to the table holding Email objects
        """
        self.drop_table(f'{table_name}')
        self.create_table(f'{table_name}', {
            'email_id'         :'INT PRIMARY KEY',
            'sender'           :'TEXT',
            'receiver'         :'TEXT',
            'subject'          :'TEXT',
            'body'             :'TEXT',
            'email_date'       :'TEXT',
            'first_email'      :'INT',
            'reply_email'      :'INT',
            'fwd_email'        :'INT',
            'clean_body'       :'TEXT',
            'conversation_id'  :'TEXT'
            } )

    def insert_email(self, email_obj, table_name):
        """Insert <Email objects> into the database"""        
        data = (email_obj.id, email_obj.sender, email_obj.receiver, email_obj.subject, 
                email_obj.body, email_obj.clean_body, email_obj.date, email_obj.first_email, 
                email_obj.reply_email, email_obj.fwd_email, email_obj.conversation_id)

        self.db.execute(f'INSERT INTO {table_name} \
                                        (email_id, sender, receiver, subject, body, clean_body \
                                        , email_date , first_email, reply_email \
                                        , fwd_email, conversation_id) \
                                    values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
        self.db.commit()

    # issues
    def create_issues_table(self, table_name='issues'):
        """
        Creates a table to store <Issue objects> from IssueParser.
        Knows about their attributes and creates the corresponding columns.

        :param table_name : name given to the table holding <Issue objects>
        """
        self.drop_table(f'{table_name}')
        self.create_table(f'{table_name}', {
            'issue_id'      :'INT PRIMARY KEY',
            'title'         :'TEXT',
            'state'         :'TEXT',
            'creator'       :'TEXT',
            'created_at'    :'TEXT',
            'comments'      :'INT',
            'body'          :'TEXT',
            'clean_body'    :'TEXT'
            } )

    def insert_issue(self, issue_obj, table_name):
        """Insert <Issue objects> into the database"""        
        data = (issue_obj.issue_id, issue_obj.title, issue_obj.state, issue_obj.creator, 
                issue_obj.created_at, issue_obj.comments, issue_obj.body, issue_obj.clean_body)
        self.db.execute(f'INSERT INTO {table_name} \
                                        (issue_id, title, state, creator, created_at \
                                        , comments, body, clean_body) \
                                    values(?, ?, ?, ?, ?, ?, ?, ?)', data)
        self.db.commit()

    # issue comments
    def create_issue_comments_table(self, table_name='issue_comments'):
        """
        Creates a table to store <IssueComment objects> objects from 
        IssueCommentParser.Knows about their attributes and creates the 
        corresponding columns.

        :param table_name : name given to the table holding <IssueComment obj>
        """
        self.drop_table(f'{table_name}')
        self.create_table(f'{table_name}', {
            'comment_id'    :'INT PRIMARY KEY',
            'issue_id'      :'INT',
            'creator'       :'TEXT',
            'created_at'    :'TEXT',
            'body'          :'TEXT',
            'clean_body'    :'TEXT',
            'FOREIGN KEY (issue_id)' : 'REFERENCES issues (issue_id)'
            } )


    def insert_issue_comment(self, issue_comment_obj, table_name):
        """Insert <IssueComment objects> into the database"""        
        data = (issue_comment_obj.comment_id, issue_comment_obj.issue_id, issue_comment_obj.creator, 
                issue_comment_obj.created_at, issue_comment_obj.body, issue_comment_obj.clean_body)
        self.db.execute(f'INSERT INTO {table_name} \
                                        (comment_id, issue_id, creator, created_at \
                                         , body, clean_body) \
                                    values(?, ?, ?, ?, ?, ?)', data)
        self.db.commit()

    # rucio docs
    def create_docs_table(self, table_name='docs'):
        """
        Creates a table to store <RucioDoc objects> objects from 
        RucioDocsParser.

        :param table_name : name given to the table holding <RucioDoc obj>
        """
        self.drop_table(f'{table_name}')
        self.create_table(f'{table_name}', {
            'doc_id'    :'INT PRIMARY KEY',
            'name'      :'INT',
            'url'       :'TEXT',
            'body'      :'TEXT',
            'doc_type'  :'TEXT'
            } )


    def insert_doc(self, docs_obj, table_name):
        """Insert <IssueComment objects> into the database"""        
        data = (docs_obj.doc_id, docs_obj.name, docs_obj.url, 
                docs_obj.body, docs_obj.doc_type)
        self.db.execute(f'INSERT INTO {table_name} \
                            (doc_id, name, url, body, \
                            doc_type) \
                            values(?, ?, ?, ?, ?)', data)
        self.db.commit()
    
   # questions
    def create_question_table(self, table_name='questions'):
        """
        Creates a table to store <Question objects> objects from 
        QuestionDetector.

        :param table_name : name given to the table holding <Question obj>
        """
        self.drop_table(f'{table_name}')
        self.create_table(f'{table_name}', {
             'question_id' : 'TEXT PRIMARY KEY',
             'question'    : 'TEXT',
             'start'       : 'TEXT',
             'end'         : 'TEXT',
             'context'     : 'TEXT',
             'email_id'    : 'INT',
             'issue_id'    : 'INT',
             'comment_id'  : 'INT',
             'FOREIGN KEY (email_id)' : 'REFERENCES emails (email_id)',
             'FOREIGN KEY (issue_id)' : 'REFERENCES issues (issue_id)',
             'FOREIGN KEY (comment_id)' : 'REFERENCES issue_comments (comment_id)'
             })

    def insert_question(self, question_obj, table_name='questions'):
        """Insert question into the database"""
        data = (question_obj.id, question_obj.question,
                question_obj.start, question_obj.end,
                question_obj.context, question_obj.email_id,
                question_obj.issue_id, question_obj.comment_id)

        self.db.execute(f'INSERT INTO {table_name} \
                                    (question_id, question, start,\
                                     end, context, email_id, issue_id, \
                                     comment_id) \
                                     values(?, ?, ?, ?, ?, ?, ?, ?)', data)
        self.db.commit()
        