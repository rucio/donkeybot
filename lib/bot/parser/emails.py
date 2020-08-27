# bot modules
import bot.utils as utils
import bot.config as config
from bot.database.sqlite import Database
from bot.parser.interface import IParser

# general python
import pandas as pd
import pickle
import hashlib
import re
import sys
from tqdm import tqdm


class Email:
    """Email object"""

    def __init__(
        self,
        email_id,
        sender,
        receiver,
        subject,
        body,
        email_date,
        first_email,
        reply_email,
        fwd_email,
        clean_body,
        conversation_id,
    ):
        # email data
        self.id = email_id
        self.sender = sender
        self.receiver = receiver
        self.subject = subject
        self.body = body
        self.date = email_date
        self.first_email = first_email
        self.reply_email = reply_email
        self.fwd_email = fwd_email
        self.clean_body = clean_body
        self.conversation_id = conversation_id
        # checks
        self._check_sender()

    def __str__(self):
        return f'subject ="{self.subject}"; email_id ="{self.id}"; conversation ="{self.conversation_id}"'

    def _check_sender(self):
        """Keeps the single email sender or raises an error if multiple exist"""
        try:
            if len(self.sender) > 1:
                raise MultipleSendersError(
                    f"There are more than one senders in {id(self)}"
                )
            else:
                # was a list thus [0]
                self.sender = self.sender[0]
        except MultipleSendersError as _e:
            sys.exit(_e)


class MultipleSendersError(Exception):
    """Raised when there are more than one senders in an email"""

    pass


class EmailParser(IParser):
    """Email Parser"""

    def __init__(self):
        self.type = "Email Parser"
        self._get_conversation_dict()

    def _get_conversation_dict(self, dict_name="conversation_dict"):
        """Load the email conversations dictionary."""
        try:
            with open(config.DATA_DIR + f"{dict_name}.pickle", "rb") as f:
                self.conversation_dict = pickle.load(f)
        except Exception as _e:
            self.conversation_dict = {}
            print(f"Error : Could not load {dict_name}.")
            print(_e)

    def parse(
        self,
        sender,
        receiver,
        subject,
        body,
        date,
        db=Database,
        emails_table_name="emails",
    ):
        """
        Parses a single email.

        <!> Note : Conversation dictionary must already exist so that email's conversation is matched
        correctly. To create this dictionary run the initial fetched emails dataframe
        through the parser with the .parse_dataframe() method.

        :param [sender,...,date]  : all the raw email attributes
        :param db                 : bot Database object to where we store the parsed emails
        :param emails_table_name  : in case we need use a different table name (default 'emails')
        :returns email            : Email object 
        """
        # new id is num of emails in our database incremented by one. (works for the first inserted email as well)
        email_id = int(db.query(f"""SELECT COUNT(email_id) FROM {emails_table_name}""")[0][0]) + 1
        email_sender = list(re.findall("<(.*?)>", sender))
        email_receiver = ", ".join(list(re.findall("<(.*?)>", receiver)))
        email_subject = subject
        email_body = body
        # '%a, %d %b %Y %H:%M:%S %z' is the date format we find in Rucio Emails
        email_date = utils.convert_to_utc(date, "%a, %d %b %Y %H:%M:%S %z")
        (email_is_reply, email_is_fwd, email_is_first) = self.find_category(subject)
        email_clean_body = self.clean_body(body)
        email_clean_subject = self.clean_subject(subject)
        email_conversation_id = self.find_conversation(subject)

        email = Email(
            email_id=email_id,
            sender=email_sender,
            receiver=email_receiver,
            subject=email_subject,
            body=email_body,
            email_date=email_date,
            first_email=email_is_first,
            reply_email=email_is_reply,
            fwd_email=email_is_fwd,
            clean_body=email_clean_body,
            conversation_id=email_conversation_id,
        )

        db.insert_email(email, table_name=emails_table_name)
        return email

    def parse_dataframe(
        self,
        emails_df=pd.DataFrame,
        db=Database,
        emails_table_name="emails",
        return_emails=False,
    ):
        """
        Parses the entire fetched emails dataframe, creates Email objects and saves them to db.
        
        <!> Note  : While parsing the dataframe we are also going to create the email
        conversation which will be held in a conversation dictionary stored as a pickle file.

        :param emails_df     : pandas DataFrame object containing all emails
        :param db            : bot Database object to save the Email objects
        :param return_emails : Boolean -> if we return a list of Email objects (default False)
        :returns emails      : list of Email objects 
        """
        self.create_conversations(emails_df)

        print("Parsing emails...")
        emails = []
        for i in tqdm(range(len(emails_df.index))):
            email = self.parse(
                sender=emails_df.sender.values[i],
                receiver=emails_df.receiver.values[i],
                subject=emails_df.subject.values[i],
                body=emails_df.body.values[i],
                date=emails_df.date.values[i],
                db=db,
                emails_table_name=emails_table_name,
            )
            if return_emails:
                emails.append(email)
            else:
                continue
        return emails

    @staticmethod
    def clean_subject(subject):
        """
        Cleans an email's subject for use in other methods.

        1) lower
        2) remove REGEX_METACHARACTRERS
        3) remove starting fwd:
        4) remove starting re:

        :returns clean_email_subject : cleaned email subject
        """
        clean_email_subject = utils.remove_chars(
            subject.lower(), config.REGEX_METACHARACTERS
        ).lstrip()
        clean_email_subject = re.sub("^(fwd:)", "", clean_email_subject).lstrip()
        clean_email_subject = re.sub("^(re:)", "", clean_email_subject).lstrip()
        return clean_email_subject

    def find_conversation(self, subject, dict_name="conversation_dict"):
        """
        Finds the corresponding conversation_id based on the email's subject.
        Search the self.conversation_dict for existing conversation matching the
        cleaned subject of the email. If needed create a new conversation.
                       
        <!> Note: If a reply email doesn't exist then the conversation is not created
        any emails that don't have replies will end up with conversation_id == None
        
        :param subject           : email's subject 
        :format conversation_id  : "cid_<md5hash>" or None
        :returns conversation_id : the conversation_id for the email's subject
        """
        clean_email_subject = self.clean_subject(subject)

        (email_is_reply, email_is_fwd, email_is_first) = self.find_category(subject)
        if clean_email_subject in self.conversation_dict:
            conversation_id = self.conversation_dict[clean_email_subject]
        elif email_is_reply:
            conversation_id = (
                "cid_"
                + hashlib.md5(str(clean_email_subject).encode("utf-8")).hexdigest()[:6]
            )
            self.conversation_dict[clean_email_subject] = conversation_id
            utils.save_dict(f"{dict_name}", self.conversation_dict)
        else:
            conversation_id = None
        return conversation_id

    @staticmethod
    def clean_body(body):
        """
        Cleans the email's body.

        Applies the following:
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
        # steps 1-4 done with utils.pre_process_text function
        clean_email_body = utils.pre_process_text(
            body, fix_url=True, remove_newline=True
        )
        # match the 4 regex patterns
        try:
            start_1 = start_2 = start_3 = start_4 = None
            if config.ON_HDR_REGEX.search(clean_email_body) is not None:
                for on_hdr_match in config.ON_HDR_REGEX.finditer(clean_email_body):
                    start_1 = on_hdr_match.start()
                    break
            if config.ORIGINAL_MSG_REGEX.search(clean_email_body) is not None:
                for or_msg_match in config.ORIGINAL_MSG_REGEX.finditer(
                    clean_email_body
                ):
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

            # if any matches keep text up to the earliest/first match
            if all(start is None for start in [start_1, start_2, start_3, start_4]):
                return clean_email_body
            else:
                min_start = min(
                    start
                    for start in [start_1, start_2, start_3, start_4]
                    if start is not None
                )
                clean_email_body = clean_email_body[:min_start]
                return clean_email_body
        except Exception as _e:
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
        clean_email_subject = utils.remove_chars(
            subject.lower(), config.REGEX_METACHARACTERS
        ).lstrip()
        clean_email_subject = re.sub("^(fwd:)", "", clean_email_subject).lstrip()
        clean_email_subject = re.sub("^(re:)", "", clean_email_subject).lstrip()
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
        is_reply = re.search("^re:", subject.lower())
        is_fwd = re.search("^fwd:", subject.lower())
        if is_reply:
            reply_email = 1
            fwd_email = 0
            first_email = 0
        elif is_fwd:
            reply_email = 0
            fwd_email = 1
            first_email = 0
        else:
            reply_email = 0
            fwd_email = 0
            first_email = 1
        return reply_email, fwd_email, first_email

    ##TODO improve code quality of create_conversations() method
    def create_conversations(self, emails_df, dict_name="conversation_dict"):
        """
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
        """
        print("Creating conversation dictionary...")
        emails_df["reply_email"] = emails_df.subject.apply(
            lambda x: x.lower()
        ).str.contains("^re:", na=False)
        self.conversation_dict = {}
        emails_df["subject"] = emails_df["subject"].apply(
            lambda x: utils.remove_chars(x.lower(), config.REGEX_METACHARACTERS)
        )
        reply_emails = emails_df[emails_df["reply_email"] == True]
        for i, re_subject in enumerate(reply_emails.subject):
            subject = re.sub("^(re:)", "", re_subject).lstrip()
            conversation_id = (
                "cid_" + hashlib.md5(str(subject).encode("utf-8")).hexdigest()[:6]
            )
            self.conversation_dict[subject] = conversation_id

        utils.save_dict(f"{dict_name}", self.conversation_dict)
        return self.conversation_dict
