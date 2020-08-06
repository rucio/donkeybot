# bot modules
from bot.database import Database
import bot.config as config
import bot.helpers as helpers
# general python
from abc import ABCMeta, abstractmethod
import pandas as pd
import hashlib
import re
import sys
from tqdm import tqdm

## Interface and Factory definitions
class IParser(metaclass=ABCMeta):
    """The Parser Interface"""
    
    @abstractmethod
    def parse():
        """Parses a single data point instance."""
        pass

    @abstractmethod
    def parse_dataframe():
        """Parses the full dataframe of the data."""
        pass


class ParserFactory():

    @staticmethod
    def get_parser(data_type):
        """
        Select between 
        - Issue
        - Issue Comment
        - Rucio Documentation
        - Email

        :returns parser: a <Parser object> 
        """

        try:
            if data_type == 'Issue':
                return IssueParser()
            if data_type == 'Issue Comment':
                return IssueCommentParser()
            if data_type == 'Rucio Documentation':
                return RucioDocsParser()
            if data_type == 'Email':
                return EmailParser()
            raise AssertionError("Parser not found")
        except AssertionError as _e:
            print(_e)


## Emails
class Email:

    def __init__(self, email_id, sender, receiver, subject, body,\
        email_date, first_email, reply_email, fwd_email, clean_body, conversation_id ):
        # email data
        self.id              = email_id
        self.sender          = sender
        self.receiver        = receiver
        self.subject         = subject
        self.body            = body
        self.date            = email_date
        self.first_email     = first_email
        self.reply_email     = reply_email
        self.fwd_email       = fwd_email
        self.clean_body      = clean_body
        self.conversation_id = conversation_id
        # checks         
        self._check_sender()
        

    def __str__(self): 
        return f'subject ="{self.subject}"; email_id ="{self.id}"; conversation ="{self.conversation_id}"'
    

    def _check_sender(self):
        """Keeps the single email sender or raises an error if multiple exist"""

        try:
            if len(self.sender) > 1:
                raise MultipleSendersError(f"There are more than one senders in {id(self)}")
            else:
                # was a list thus [0]
                self.sender = self.sender[0]
        except MultipleSendersError as _e:
            sys.exit(_e)



class EmailParser(IParser):

    def __init__(self):
        self.type = 'Email Parser'

    def parse(self, sender, receiver, subject, body, date, db = Database, emails_table_name='emails'):
        """
        Parses a single email

        <!> Note   : The parse() method is only expected to be used after an an emails table
        has been created in the db. To create said table use the Database object's 
        .create_emails_table() method

        <!> Note 2 : While parsing a single email we expect the conversation dictionary
        to already have been created so that we can try and find the conversation this
        email should be a part of. To create this dictionary run the initial fetched emails dataframe
        through the parser with the .parse_dataframe() method.

        :param [sender,...,date]  : all the raw email attributes
        :param db                 : <bot Database object> to where we store the parsed emails
        :param emails_table_name  : in case we need use a different table name (default 'emails')
        :returns email            : <Email object> 
        """

        # new id is num of emails in our database incremented by one. (works for the first inserted email as well)
        email_id                = int(db.query(f'''SELECT COUNT(email_id) FROM emails''')[0][0]) + 1
        email_sender            = list(re.findall('<(.*?)>', sender))
        email_receiver          = ', '.join(list(re.findall('<(.*?)>', receiver)))
        email_subject           = subject
        email_body              = body
        # '%a, %d %b %Y %H:%M:%S %z' is the date format we find in Rucio Emails
        email_date              = helpers.convert_to_utc(date, '%a, %d %b %Y %H:%M:%S %z') 
        (email_reply_ind, email_fwd_ind, email_first_ind) = self.find_category(subject)
        email_clean_body        = self.clean_body(body)
        email_clean_subject     = self.clean_subject(subject)
        # we need to match the conversation of this email to the existing ones 
        email_conversation_id   = self.find_conversation(subject)

        # create and return a single email instance
        email = Email(email_id        = email_id,
                      sender          = email_sender,
                      receiver        = email_receiver,
                      subject         = email_subject,
                      body            = email_body,
                      email_date      = email_date,
                      first_email     = email_first_ind,
                      reply_email     = email_reply_ind,
                      fwd_email       = email_fwd_ind,
                      clean_body      = email_clean_body,
                      conversation_id = email_conversation_id)
        
        # insert the email to the db
        db.insert_email(email, table_name=emails_table_name)
        return email
    

    def parse_dataframe(self, emails_df=pd.DataFrame, db=Database, emails_table_name='emails', return_emails=False):
        """
        Parses the entire fetched emails dataframe, creates <Email objects> and saves them to db.
        
        Expects a <pandas DataFrame object> as input that holds the raw fetched emails.
        
        <!> Note  : While parsing the dataframe we are also going to create the email
        conversation which will be held in a conversation dictionary stored as a pickle
        file.

        :param emails_df     : <pandas DataFrame object> containing all emails
        :param db            : a <bot Database object> to save the <Email objcets>
        :param return_emails : True/False on if we return a list of <Email objects> (default False)
        :returns emails      : a list of <Email objects> created by the EmailParser 
        """

        # step 1 is creating the conversation dictionary based on all the emails
        self.create_conversations(emails_df)
        print("Parsing emails...")
        emails = []
        # step 2 is parsing the entire dataframe 
        for i in tqdm(range(len(emails_df.index))):
            email = self.parse(sender = emails_df.sender.values[i],
                               receiver = emails_df.receiver.values[i],
                               subject = emails_df.subject.values[i],
                               body = emails_df.body.values[i],
                               date = emails_df.date.values[i], 
                               db = db,
                               emails_table_name=emails_table_name)
            if return_emails:
                emails.append(email)
            else:
                continue
        return emails

    

    @staticmethod
    def clean_subject(subject):
        """
        Applies the following to the email's subject:
        1) lower
        2) remove REGEX_METACHARACTRERS
        3) remove starting fwd:
        4) remove starting re:

        :returns clean_email_subject : cleaned email subject
        """ 
        
        clean_email_subject = helpers.remove_chars(subject.lower(), config.REGEX_METACHARACTERS).lstrip()
        clean_email_subject = re.sub('^(fwd:)', '', clean_email_subject).lstrip()
        clean_email_subject = re.sub('^(re:)', '', clean_email_subject).lstrip()
        return clean_email_subject


    def find_conversation(self, subject):
        """
        Finds the corresponding conversation_id based on the email's subject.

        Search the CONVERSATION_DICT for existing conversation matching the
        cleaned subject of the email. If needed create a new conversation.
                       
        <!> Note: If a reply email doesn't exist then the conversation is not created
        any emails that don't have replies will end up with conversation_id == None
        
        :param subject           : email's subject 
        :format conversation_id  : "cid_<md5hash>" or None
        :returns conversation_id : the conversation_id for the email's subject
        """      

        clean_email_subject = self.clean_subject(subject)
        # we need to know if its a reply email
        (email_reply_ind, email_fwd_ind, email_first_ind) = self.find_category(subject)
        # if the conversation exists
        if clean_email_subject in config.CONVERSATION_DICT:
            conversation_id = config.CONVERSATION_DICT[clean_email_subject]
        # if it's a reply email append the new conversation to the saved dictionary
        elif email_reply_ind:
            conversation_id = 'cid_'+hashlib.md5(str(clean_email_subject).encode('utf-8')).hexdigest()[:6]
            config.CONVERSATION_DICT[clean_email_subject] = conversation_id
            helpers.save_dict('conversation_dict', config.CONVERSATION_DICT)   
        # conversation doesn't exist
        else:
            conversation_id = None
        return conversation_id


    @staticmethod
    def clean_body(body):
        """
        Applies the following to the email's body:
        1) Remove newline characters from inside urls
        2) Replace newline characters with ' ' space 
        3) Remove extra whitespaces
        4) Decontract words
        5) Try to find matches based on the regex patterns.
           If said matches exist, only keep the text up to the
           earliest match. These patterns are inside emails right 
           before text from previous emails is pasted/quoted.
           eg.
           Example of a reply email:
                "Dear Nick
                        ...
                 Thanks, George.
                 On <DATE> Nick wrote: 
                    >> Previous email body
                    >> Previous email body "
            
            from which we only keep:
                "Dear Nick
                        ...
                 Thanks, George."

        :param  body        : body of an email 
        :returns clean_email_body : cleaned body of an email
        """

        # steps 1-4 done with helpers.pre_process_text function
        clean_email_body = helpers.pre_process_text(body, 
                                                    fix_url = True,
                                                    remove_newline = True,
                                                    decontract_words = True
                                                    )
        # match the 4 regex patterns
        try:
            start_1 = start_2 = start_3 = start_4 = None
            if config.ON_HDR_REGEX.search(clean_email_body) is not None:
                for on_hdr_match in config.ON_HDR_REGEX.finditer(clean_email_body):
                    start_1 = on_hdr_match.start()
                    break
            if config.ORIGINAL_MSG_REGEX.search(clean_email_body) is not None:
                for or_msg_match in config.ORIGINAL_MSG_REGEX.finditer(clean_email_body):
                    start_2 = or_msg_match.start()
                    break
            if config.QUOTED_REGEX.search(clean_email_body) is not None:
                for quote_match in config.QUOTED_REGEX.finditer(clean_email_body):
                    start_3 = quote_match.start()
                    break           
            if config.HEADER_REGEX.search(clean_email_body) is not None:
                for hdr_match in config.HEADER_REGEX.finditer(clean_email_body):
                    start_4 = hdr_match.start()
                    break
            
            # if found keep text up to the first match
            if all(start is None for start in [start_1, start_2, start_3, start_4]):
                return clean_email_body
            else:
                min_start = min(start for start in [start_1, start_2, start_3, start_4] if start is not None)
                clean_email_body = clean_email_body[:min_start]
                return clean_email_body
        except _e:
            print(_e)



    @staticmethod
    def clean_subject(subject):
        """
        Applies the following to the email's subject:
        1) lower
        2) remove REGEX_METACHARACTRERS
        3) remove starting fwd:
        4) remove starting re:

        :returns clean_email_subject : cleaned email subject
        """ 
        
        clean_email_subject = helpers.remove_chars(subject.lower(), config.REGEX_METACHARACTERS).lstrip()
        clean_email_subject = re.sub('^(fwd:)', '', clean_email_subject).lstrip()
        clean_email_subject = re.sub('^(re:)', '', clean_email_subject).lstrip()
        return clean_email_subject



    @staticmethod
    def find_category(subject):
        """
        Finds if email is categorized as a reply, first, or forwarded 
        based on the subject
        
        <!> Note: sqlite doesn't support Boolean so 0/1 integer was chosen

        : param subject     : the subject of the email that will help us find it's
                              category
        : type first_email  : 0 / 1 INT
        : type reply_email  : 0 / 1 INT
        : type fwd_email    : 0 / 1 INT
        : returns           : reply_email, fwd_email, first_email
        """
        
        reply_match = re.search('^re:', subject.lower())
        fwd_match = re.search('^fwd:', subject.lower())
        if reply_match:
            reply_email = 1
            fwd_email   = 0
            first_email = 0
        elif fwd_match:
            reply_email = 0
            fwd_email   = 1
            first_email = 0
        else:
            reply_email = 0
            fwd_email   = 0
            first_email = 1
        return reply_email, fwd_email, first_email


    ##TODO improve code quality of create_conversations() method
    @staticmethod
    def create_conversations(emails_df):
        '''
        Creates and saves a conversation dictionary containing an id and
        the corresponding subject based on the input emails dataframe.

        Step 0 : Distinguish reply emails
        Step 1 : lower subject
        Step 2 : remove regex_metacharacters
        Step 3 : On the reply emails exist get the subject (without Re:)
                hash it and create conversation_id
        Step 4 : return conversation_dict
        
        <!> Note: If a reply email doesn't exist then the conversation is not created
        any emails that don't have replies will end up with conversation_id == None

        :return conversation_dict : dict of keys = email_subject, values = conversation_id
        '''    

        print("Creating conversation dictionary...")
        # find out which emails are replies
        emails_df['reply_email'] = emails_df.subject.apply(lambda x: x.lower()).str.contains("^re:", na=False)
        conversation_dict = {}
        emails_df['subject'] = emails_df['subject'].apply(lambda x: helpers.remove_chars(x.lower(), config.REGEX_METACHARACTERS))
        reply_emails = emails_df[emails_df['reply_email'] == True]
        for i, re_subject in enumerate(reply_emails.subject):
            subject = re.sub('^(re:)', '', re_subject).lstrip()
            conversation_id = 'cid_'+hashlib.md5(str(subject).encode('utf-8')).hexdigest()[:6]
            conversation_dict[subject] = conversation_id
        
        # save the conversation_dict created
        helpers.save_dict('conversation_dict', conversation_dict)
        return conversation_dict


class MultipleSendersError(Exception):
    """Raised when there are more than one senders in an email"""
    pass


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


## Issues
class Issue():
    """A GitHub Issue"""

    def __init__(self, issue_id, title, state, creator, created_at, comments, body, clean_body):
        self.issue_id   = int(issue_id)
        self.title      = title
        self.state      = state
        self.creator    = creator
        self.created_at = created_at
        self.comments   = int(comments)
        self.body       = body
        self.clean_body = clean_body


class IssueParser(IParser):

    def __init__(self):
        self.type = 'Issue Parser'

    def parse(self, issue_id, title, state, creator, created_at, comments, body, db = Database, issues_table_name='issues'):
        """
        Parses a single issue
        
        <!> Note  : The parse() method is only expected to be used after an an issues table
        has been created in the db. To create said table use the Database object's 
        .create_issues_table() method before attempting to parse.
        
        :param [issue_id,...,body]  : all the raw issue attributes
        :param db                 : <bot Database object> to where we store the parsed issues
        :param issues_table_name  : in case we need use a different table name (default 'issues')
        :returns issue            : an <Issue object> created by the IssueParser
        """

        # The date format returned from the GitHub API is in the ISO 8601 format: "%Y-%m-%dT%H:%M:%SZ" 
        issue_created_at  = helpers.convert_to_utc(created_at, '%Y-%m-%dT%H:%M:%SZ') 
        # lower/decontract/fix_urls/clean ISSUE_TEMPLATE patterns
        # if additional textprocessing is needed we can always change it here
        issue_clean_body = helpers.pre_process_text(self.clean_issue_body(body),
                                                    fix_url=True,
                                                    decontract_words=True)
        issue = Issue(issue_id    = issue_id, 
                      title       = title, 
                      state       = state, 
                      creator     = creator,
                      created_at  = issue_created_at,
                      comments    = comments,
                      body        = body, 
                      clean_body  = issue_clean_body)

        # insert the issue to the db
        if issue.comments > 0: # if no comments in issue then there won't be any comments. No need to save it
            db.insert_issue(issue, table_name=issues_table_name)
        return issue


    def parse_dataframe(self, issues_df=pd.DataFrame, db=Database, issues_table_name='issues', return_issues=False):
        """
        Parses the entire fetched issues dataframe, creates <Issue objects> and saves them to db.
        
        Expects a <pandas DataFrame object> as input that holds the raw fetched issues.
        For more information about the structure and content of issues_df look at the IssueFetcher.

        :param issues_df     : <pandas DataFrame object> containing all issues
        :param db            : <bot Database object> to save the <Issue objects>
        :param return_issues : True/False on if we return a list of <Issue objects> (default False)
        :returns issues      : a list of <Issue objects> created by the IssueParser 
        """

        issues = []
        print("Parsing issues...")
        for i in tqdm(range(len(issues_df.index))):
            issue = self.parse(issue_id          = issues_df.issue_id.values[i],
                               title             = issues_df.title.values[i],
                               state             = issues_df.state.values[i],
                               creator           = issues_df.creator.values[i],
                               created_at        = issues_df.created_at.values[i], 
                               comments          = issues_df.comments.values[i], 
                               body              = issues_df.body.values[i], 
                               db                = db,
                               issues_table_name = issues_table_name)
            if return_issues:
                issues.append(issue)
            else:
                continue
        return issues


    @staticmethod
    def clean_issue_body(body):
        """ 
        Cleans up the body of an issue from 
        ISSUE_TEMPLATE patterns in Rucio.

        :returns clean_body : cleaned issue body
        """

        clean_body = body.strip('/n/r')\
                    .replace('Motivation\r', '')\
                    .replace('Modification\r', '')\
                    .replace('Expected behavior\r', '')\
                    .replace('\n', ' ')\
                    .replace('\r', ' ')\
                    .replace('-', ' ')\
                    .strip()  
        clean_body = re.sub(' +', ' ', clean_body).strip(' ')
        return clean_body


## Issue Comments
class IssueComment():
    """A GitHub Issue comment"""

    def __init__(self, issue_id, comment_id, creator, created_at, body, clean_body):
        self.issue_id   = int(issue_id)
        self.comment_id = int(comment_id)
        self.creator    = creator
        self.created_at = created_at
        self.body       = body
        self.clean_body = clean_body

class IssueCommentParser(IParser):

    def __init__(self):
        self.type = 'Issue Comment Parser'

    def parse(self, issue_id, comment_id, creator, created_at, body, db=Database, issue_comments_table='issue_comments'):
        """
        Parses a single issue comment
        
        <!> Note  : The parse() method is only expected to be used after an an issue comments table
        has been created in the db. To create said table use the Database object's 
        .create_issue_comments_table() method before attempting to parse.
        
        :param [issue_id,...,body]   : all the raw issue comment's attributes
        :param db                    : <bot Database object> to where we store the parsed issue comments
        :param issue_comments_table  : in case we need use a different table name (default 'issue_comments')
        :returns issue_comment       : an <IssueComment object> created by the IssueCommentParser
        """

        # The date format returned from the GitHub API is in the ISO 8601 format: "%Y-%m-%dT%H:%M:%SZ" 
        issue_comment_created_at  = helpers.convert_to_utc(created_at, '%Y-%m-%dT%H:%M:%SZ') 
        # lower/decontract/fix_urls/remove_newline
        # if additional textprocessing is needed we can always change it here
        issue_comment_clean_body = helpers.pre_process_text(body,
                                                            fix_url=True,
                                                            remove_newline=True,
                                                            decontract_words=True)
        issue_comment = IssueComment(issue_id   = issue_id, 
                                     comment_id = comment_id, 
                                     creator    = creator, 
                                     created_at = issue_comment_created_at,
                                     body       = body,
                                     clean_body = issue_comment_clean_body)

        # insert the issue comment to the db
        db.insert_issue_comment(issue_comment, table_name=issue_comments_table)
        return issue_comment


    def parse_dataframe(self, comments_df=pd.DataFrame, db=Database, issue_comments_table='issue_comments', return_comments=False):
        """
        Parses the entire fetched issue comments dataframe, creates <IssueComment objects> and saves them to db.
        
        Expects a <pandas DataFrame object> as input that hold the raw fetched issues.
        For more information about the structure and content of comments_df look at the IssueFetcher.

        :param comments_df       : <pandas DataFrame object> containing all issue comments
        :param db                : <bot Database object> to save the <IssueComment objects>
        :param return_comments   : True/False on if we return a list of <IssueComment objects> (default False)
        :returns issue_comments  : a list of <IssueComment objects> created by the IssueCommentParser 
        """

        issue_comments = []
        print("Parsing issue comments...")
        for i in tqdm(range(len(comments_df.index))):
            issue_comment = self.parse(issue_id             = comments_df.issue_id.values[i],
                                       comment_id           = comments_df.comment_id.values[i],
                                       creator              = comments_df.creator.values[i],
                                       created_at           = comments_df.created_at.values[i],
                                       body                 = comments_df.body.values[i],
                                       db                   = db,
                                       issue_comments_table = issue_comments_table)
            if return_comments:
                issue_comments.append(issue_comment)
            else:
                continue
        return issue_comments






################################################################################ 

if __name__ == '__main__': 
    pass