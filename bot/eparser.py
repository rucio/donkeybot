# bot modules
from bot.database import Database
import bot.config as config
import bot.helpers as helpers
# general python
import hashlib
import re
from datetime import datetime 
import pytz
import sys

class EmailParser:
    """
    Parses Email Objects
    attributes:
        :id                 : a unique id for the email (int) 
        :sender             : email's sender
        :receiver           : email's receiver
        :subject            : email's subject
        :body               : email's body
        :date               : email's date
        :first_email        : 0/1 if the email is the first sent in a conversation (not reply or fwd)
        :reply_email        : 0/1 if the email is a reply to another email
        :fwd_email          : 0/1 if the email is something forwarded
        :clean_body         : clean body of the email which has \\n newline removed and any quoted 
                              text from past emails also removed, which is present in reply emails
        :conversation_id    : an id unique to each distinct conversation discussed. For a conversation
                              to exist there need to be at least one reply and the conversation_ids are
                              created based on the subject of each email (look at dataset_creation.py)
    """

    def __init__(self, email_id, sender, receiver, subject, body, date):
        self.id = int(email_id)
        self.sender = list(re.findall('<(.*?)>', sender))
        self._check_senders()
        self.receiver = ', '.join(list(re.findall('<(.*?)>', receiver)))
        self.subject = subject
        self.body = body
        self.date = date
        self._convert_date() 
        self._find_category()
        self._clean_body() 
        self._clean_subject() 
        self._find_conversation() 
        self._check_conversation()


    def __str__(self): 
        return f'subject ="{self.subject}"; conversation_id ="{self.conversation_id}"'


    def _convert_date(self):
        """
        Converts date to UTC
        
        :type date : String in utc format
        """
        
        self.date = datetime.strptime(self.date, '%a, %d %b %Y %H:%M:%S %z')
        self.date = self.date.replace(tzinfo=pytz.UTC)- self.date.utcoffset()
        return


    def _clean_body(self):
        """
        Applies the following to the email's body:
        1) Remove \\n from inside urls
        2) Replace \\n with space 
        3) Make sure no extra spaces exist
        4) Try to find matches based on the regex patterns.
           If said matches exist, only keep the text up to the
           ealiest match. These patterns are inside emails right 
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

        :type clean_body : String
        """
        
        self.clean_body = helpers.fix_urls(self.body)
        self.clean_body = self.clean_body.replace('\n', ' ')
        ' '.join(self.clean_body.split())

        # match the 4 regex patterns
        try:
            start_1 = start_2 = start_3 = start_4 = None
            if config.ON_HDR_REGEX.search(self.clean_body) is not None:
                for on_hdr_match in config.ON_HDR_REGEX.finditer(self.clean_body):
                    start_1 = on_hdr_match.start()
                    break
            if config.ORIGINAL_MSG_REGEX.search(self.clean_body) is not None:
                for or_msg_match in config.ORIGINAL_MSG_REGEX.finditer(self.clean_body):
                    start_2 = or_msg_match.start()
                    break
            if config.QUOTED_REGEX.search(self.clean_body) is not None:
                for quote_match in config.QUOTED_REGEX.finditer(self.clean_body):
                    start_3 = quote_match.start()
                    break           
            if config.HEADER_REGEX.search(self.clean_body) is not None:
                for hdr_match in config.HEADER_REGEX.finditer(self.clean_body):
                    start_4 = hdr_match.start()
                    break
            
            # if found keep text up to the first match
            if all(start is None for start in [start_1, start_2, start_3, start_4]):
                return #self.clean_body only has fixed urls and no \n
            else:
                min_start = min(start for start in [start_1, start_2, start_3, start_4] if start is not None)
                self.clean_body = self.clean_body[:min_start]
                return
        except Error:
            print(Error)
            return



    def _clean_subject(self):
        """
        Applies the following to the email's subject:
        1) lower
        2) remove REGEX_METACHARACTRERS
        3) remove starting fwd:
        4) remove starting re:

        :type clean_subject : String
        """ 
        
        self.clean_subject = helpers.remove_chars(self.subject.lower(), config.REGEX_METACHARACTERS).lstrip()
        self.clean_subject = re.sub('^(fwd:)', '', self.clean_subject).lstrip()
        self.clean_subject = re.sub('^(re:)', '', self.clean_subject).lstrip()



    def _find_conversation(self):
        """
        Search the CONVERSATION_DICT for existing conversation matching the
        cleaned_subject of self. Create it if need be.
                       
        <!> Note: If a reply email doesn't exist then the conversation is not created
        any emails that don't have replies will end up with conversation_id == None
        
        :format conversation_id : "cid_<md5hash>" or None
        """      
        
        # if the conversation exists
        if self.clean_subject in config.CONVERSATION_DICT:
            self.conversation_id = config.CONVERSATION_DICT[self.clean_subject]
            # print(f"CONVERSATION EXISTS {self.conversation_id} FOR {self.subject}")
        elif self.reply_email:
            # if it's a reply email append the new conversation
            self.conversation_id = 'cid_'+hashlib.md5(str(self.clean_subject).encode('utf-8')).hexdigest()[:6]
            config.CONVERSATION_DICT[self.clean_subject] = self.conversation_id
            helpers.save_dict('conversation_dict', config.CONVERSATION_DICT)   
            # print(f"CONVERSATION CREATED {self.conversation_id} FOR {self.subject}")
        else:
            self.conversation_id = None
            # print('CONVERSATION NON-EXISTANT')
        return


    def _check_conversation(self):
        """Checks if the conversation_id given to the email is correctly hashed"""
        
        self.correct_id = 'cid_'+hashlib.md5(str(self.clean_subject).encode('utf-8')).hexdigest()[:6]
        if self.conversation_id:
            assert self.correct_id == self.conversation_id
        else:
           pass


    def _check_senders(self):
        """Keeps the single email sender or raises an error if multiple exist"""
        try:
            if len(self.sender) > 1:
                raise MultipleSendersError(f"There are more than one senders in {id(self)}")
            else:
                self.sender = self.sender[0]
        except MultipleSendersError as _e:
            sys.exit(_e)



    def _find_category(self):
        """
        Finds if email is categorized as a reply, first, or forwarded
        
        <!> Note: sqlite doesn't support Boolean so 0/1 integer was chosen

        : type first_email  : 0 / 1 INT
        : type reply_email  : 0 / 1 INT
        : type fwd_email    : 0 / 1 INT
        """
        
        reply_match = re.search('^re:', self.subject.lower())
        fwd_match = re.search('^fwd:', self.subject.lower())
        if reply_match:
            self.reply_email = 1
            self.fwd_email = 0
            self.first_email = 0
        elif fwd_match:
            self.reply_email = 0
            self.fwd_email = 1
            self.first_email = 0
        else:
            self.reply_email = 0
            self.fwd_email = 0
            self.first_email = 1


class MultipleSendersError(Exception):
    """Raised when there are more than one senders in an email"""
    pass


    

######################################## 

if __name__ == '__main__': 
    pass
