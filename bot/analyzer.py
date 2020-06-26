# bot modules
from database import Database
import config 
import helpers 
# general python
import re
import nltk
# nltk.download("punkt")
from nltk.tokenize import PunktSentenceTokenizer

class QuestionDetector:
    """Utilizes regex patterns to match questions inside a text."""

    def __init__(self):
        # the sentence tokenizer
        self.tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer() 
        # since nltk's sentence tokenizer doesn't always work well, this regex matches questions without lowering the text 
        self.QUESTION_REGEX = re.compile(r'[A-Z][a-z][^A-Z]*[?]$') 
        # this matches questions after lowering the text
        self.LOWERED_QUESTION_REGEX = re.compile(r'(how |wh|can |could |do |does |should |would |may |is |are |have |has |will |am ).*[?]$')   
        # we can add more if we want additional exceptions
        self.EXCEPTIONS_REGEX = [config.URL_REGEX] 


    def detect(self, text):
        """
        Detect and create Question objects from input text.

        Detect the question as follows:
        1) First pattern matches questions without lowering the text
        2) Second pattern matches questions after having lowered the text

        :param text         : String upon which the detection algorithm runs (clean_body from Emails)
        :return questions   : list of Question Objects
        """
        # part 1
        questions = self._match_questions(text, self.QUESTION_REGEX)
        for i, question in enumerate(questions):
            # padding needed so that (start, end) indeces of questions are correct
            padding = ''
            for _ in text[question.start:question.end]:
                padding += ' '
            assert len(text) == len(text[:question.start] + padding + text[question.end:])
            # 'hide' already identified question and move on
            text = text[:question.start] + padding + text[question.end:]
        
        # part 2 
        lowered_text = text.lower()
        # loop needed after first run since _match_questions returns a list 
        [questions.append(match) for match in self._match_questions(lowered_text, self.LOWERED_QUESTION_REGEX)]

        return questions


    def _match_questions(self, text, pattern):
        """
        Private class function that return questions found based on input text
        and regex patterns.
        Sentence tokenization is applied before trying to match a Question.

        :param text         : text upon which the detection takes place
        :param pattern      : compiled regex pattern used to detect the questions
        :return questions   : list of Question Objects
        """
        questions = []
        # get all exceptions present in the text
        exceptions = self._get_exceptions(text)
        sentences = self.tokenizer.tokenize(text)
        sentence_indeces = list(self.tokenizer.span_tokenize(text))
        for i, sentence in enumerate(sentences):
            matches = pattern.search(sentence)
            sent_start = sentence_indeces[i][0]
            # sent_end = sentence_indeces[i][1]
            if matches is not None:
                # before appending check if the match is part of any exceptions
                if self._is_exception(exceptions, matches.group()): 
                    continue
                else:
                    q_start = sent_start + matches.start()
                    q_end = sent_start + matches.end()
                    question = Question(question_text=matches.group(), start_idx=q_start, end_idx= q_end)
                    questions.append(question)
        return questions


    def _get_exceptions(self, text):
        """
        Returns list of strings inside text that are definetely not questions based on our
        EXCEPTION_REGEX patterns.

        We can add multitude of exceptions eg. code bloacks, File, RSEs etc

        :return exceptions: list of string which we should not consider as questions
        """
        exceptions = []
        for pattern in self.EXCEPTIONS_REGEX:
            if pattern.search(text) is not None:
                for match in pattern.finditer(text):
                    exceptions.append(match.group())
        return exceptions



    @staticmethod
    def _is_exception(exceptions, question):
        """
        Check that the question found is not part of any exceptions.
        eg. URLs (only exception for now)

        :return : Boolean True/False
        """
        for exception in exceptions:
            # print("here")
            # print(exception, question.lower())
            if question.lower() in exception.lower():
                print("FOUND EXCEPTION")
                print(question, exception)
                return True
        return False


class Question:
    """
    Creates Question Objects
    attributes:
        :questions          : text of the question
        :start              : start index of the question (index in clean_body) 
        :end                : end index of the question (index in clean_body)
        :email              : email_id of the Email the question exists in
        :id                 : a unique id for the question (int)
        :clean_body         : text on which the quesiton exists in
        :conversation_id    : the conversation_id of the question's email
        :date               : the date of the question's email
        :context            : Context is the string which holds the bodies of all replies to 
                              a specific email. This feature is where the answer of a given 
                              question inside an email probably exists.        
    """
    def __init__(self, question_text, start_idx, end_idx):
        self.question = question_text
        self.start = start_idx
        self.end = end_idx


    def get_context(self):
        """
        Gets the context text for each question based on the conversation_id
        and date of each email.

        <!> Note: The email of the conversation needs to have been set before running the
        get_context() method by using the set_email() method.
        """
        if hasattr(self, 'email'):
            # open db connection
            db = Database('dataset.db', 'emails')
            # get conversation_id and the date of this question's email
            self.clean_body, self.conversation_id, self.date = db.query(f'''SELECT clean_body, conversation_id, email_date
                                  FROM emails
                                  WHERE email_id == {self.email}''')[0] # because only 1 row

            if self.conversation_id is None:
                self.context = None
            else:
                # the context is the clean body of all the following emails in the conversation 
                result =  db.query(f'''SELECT clean_body
                                       FROM emails
                                       WHERE email_id IN (
                                           SELECT email_id
                                           FROM emails
                                           WHERE conversation_id == "{self.conversation_id}"
                                                 and email_date   > "{self.date}"
                                        )
                                        ORDER BY email_date ASC
                                        ''')
                self.context = " ".join([res[0] for res in result])
            db.close_connection()
        else:
            raise QuestionEmailNotSet(f"\nError: The email_id for the Question object has not been set.Try using Question.set_email() method.")


    def set_id(self, question_id):
        """Set the question's id"""
        self.id = question_id


    def set_email(self, email_id):
        """Set the question's email id"""
        self.email = email_id


    def __str__(self):
        return f'question_text = {self.question}\nstart = {self.start}\nend = {self.end}'


class QuestionEmailNotSet(Exception):
    """Raised when the email_id for the Question object has not been set"""
    pass


########################################  
if __name__ == '__main__':
    
    # question = Question(question_text="Where are we?", start_idx=0, end_idx= 13)
    # question.set_email(64)
    # question.get_context()
    # print(question.context)

    pass
