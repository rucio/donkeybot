# bot modules
from bot.question.emails import EmailQuestion
from bot.question.issues import IssueQuestion
from bot.question.comments import CommentQuestion
import bot.config as config

# general python
import re
import nltk
from nltk.tokenize import PunktSentenceTokenizer


class QuestionDetector:
    """Utilizes regex patterns to match questions inside a text."""

    def __init__(self, detector_type=None):
        """
        Creates a QuestionDetector of some type.
        The type holds the origin of the question

        :param type: one of ['email', 'issue', 'comment']
        """

        assert detector_type in ["email", "issue", "comment"]
        self.type = detector_type
        self.tokenizer = nltk.tokenize.punkt.PunktSentenceTokenizer()
        self.QUESTION_REGEX = re.compile(r"[A-Z][a-z][^A-Z]*[?]$")
        self.LOWERED_QUESTION_REGEX = re.compile(
            r"(how |wh|can |could |do |does |should |would |may |is |are |have |has |will |am ).*[?]$"
        )
        # we can add more regexes to the list below for exceptions
        self.EXCEPTIONS_REGEX = [config.URL_REGEX]

    def detect(self, text):
        """
        Detect and create Question objects from input text.

        Detect the question as follows:
        1) First pattern matches questions without lowering the text
        2) Second pattern matches questions after having lowered the text

        :param text         : String upon which the detection algorithm runs 
        :return questions   : list of Question Objects
        """
        # part 1
        questions = self._match_questions(text, self.QUESTION_REGEX)
        for i, question in enumerate(questions):
            # padding needed so that (start, end) indexes of Question object are correct
            padding = ""
            for _ in text[question.start : question.end]:
                padding += " "
            assert len(text) == len(
                text[: question.start] + padding + text[question.end :]
            )
            # 'hide' already identified question and move on to next
            text = text[: question.start] + padding + text[question.end :]

        # part 2
        lowered_text = text.lower()
        # loop needed after first run since _match_questions returns a list (even if empty list)
        [
            questions.append(match)
            for match in self._match_questions(
                lowered_text, self.LOWERED_QUESTION_REGEX
            )
        ]
        # The reason no padding exists here is because we don't have a 3rd regex trying to match if we did
        # we would have to hide already identified questions in the text from the next pattern
        return questions

    def _create_question(self, text, start, end):
        """Creates <Question obj> based on type"""
        if self.type == "email":
            question = EmailQuestion(question_text=text, start_idx=start, end_idx=end)
        elif self.type == "issue":
            question = IssueQuestion(question_text=text, start_idx=start, end_idx=end)
        elif self.type == "comment":
            question = CommentQuestion(question_text=text, start_idx=start, end_idx=end)
        return question

    def _match_questions(self, text, pattern):
        """
        Private class function that returns questions found based on input text
        and regex patterns.
        Sentence tokenization is applied before trying to match a Question.

        :param text         : text upon which the detection takes place
        :param pattern      : compiled regex pattern used to detect the questions
        :return questions   : list of Question Objects
        """
        questions = []
        # get all exceptions present in the text
        exceptions = self._get_exception_matches(text)
        sentences = self.tokenizer.tokenize(text)
        sentence_indices = list(self.tokenizer.span_tokenize(text))
        for i, sentence in enumerate(sentences):
            matches = pattern.search(sentence)
            sent_start = sentence_indices[i][0]
            # sent_end = sentence_indices[i][1]
            if matches is not None:
                # before appending check if the match is part of any exceptions
                if self._is_exception(exceptions, matches.group()):
                    continue
                else:
                    q_start = sent_start + matches.start()
                    q_end = sent_start + matches.end()
                    question = self._create_question(
                        text=matches.group(), start=q_start, end=q_end
                    )
                    questions.append(question)
        return questions

    def _get_exception_matches(self, text):
        """
        Returns list of strings inside text that are definitely not questions based on our
        EXCEPTION_REGEX patterns.We can add multitude of exceptions 
        eg. URLs, code blocks, File, RSEs ...

        <!> Note: URLs (only exceptions matched for now)

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
        eg. URLs (only exceptions matched for now)

        :return : Boolean 
        """
        for exception in exceptions:
            if question.lower() in exception.lower():
                print("\nFound a Question exception :")
                print(question, exception)
                return True
        return False


if __name__ == "__main__":
    pass
