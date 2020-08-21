# bot modules
from bot.searcher.base import SearchEngine
from bot.searcher.question import QuestionSearchEngine
from bot.detector.answer.detector import AnswerDetector

# general python
import sys


class QAInterface:
    def __init__(
        self,
        detector=AnswerDetector,
        question_engine=QuestionSearchEngine,
        faq_engine=QuestionSearchEngine,
        docs_engine=SearchEngine,
    ):
        self.detector = detector
        self.question_engine = question_engine
        self.docs_engine = docs_engine
        self.faq_engine = faq_engine
        self._check_detector()
        self._check_engines()

    def _check_detector(self):
        try:
            assert type(self.detector) == AnswerDetector
        except AssertionError as _e:
            sys.exit(
                "Error: Wrong detector type. Make sure to use DonkeyBot's AnswerDetector."
            )

    def _check_engines(self):
        try:
            assert type(self.question_engine) == QuestionSearchEngine
            assert type(self.faq_engine) == QuestionSearchEngine
            assert type(self.docs_engine) == SearchEngine
        except AssertionError as _e:
            sys.exit(
                "Error: Wrong search engine type. Make sure to use one of DonkeyBot's Search Engines."
            )

    # TODO once FAQ table exists implement the function
    def _get_faq_answers(self, num_faqs):
        """
        Returns the most similar answers from FAQ table.

        <!> Note: AnswerDetector is not needed when matching
        through the FAQ table. The only important thing is 
        to find the most similar questions.

        :return faq_answers : list of Answer objects
        """
        # retrieved_faqs = self.faq_engine.search(self.query, num_faqs)
        return None

    def _get_question_answers(self, num_questions):
        """Returns top_k answers based on the most similar questions and their context."""
        # most similar questions
        self.retrieved_questions = self.question_engine.search(
            self.query, num_questions
        )
        print("\nRETRIEVED QUESTIONS:")
        print(self.retrieved_questions)
        question_answers = self.detector.predict(
            self.query, self.retrieved_questions, top_k=self.top_k
        )
        print("\nQUESTION ANSWERS:")
        results = {
            "question": self.query,
            "answers": [answer.__dict__ for answer in question_answers],
        }
        print(results)
        return question_answers

    def _get_docs_answers(self, num_docs):
        """Returns top_k answers based on the most similar documentation."""
        # most similar documentation docs
        self.retrieved_docs = self.docs_engine.search(self.query, num_docs)
        print("\nRETRIEVED DOCUMENTATION:")
        print(self.retrieved_docs)
        doc_answers = self.detector.predict(
            self.query, self.retrieved_docs, top_k=self.top_k
        )
        print("\nDOCUMENTATION ANSWERS:")
        results = {
            "question": self.query,
            "answers": [answer.__dict__ for answer in doc_answers],
        }
        print(results)
        return doc_answers

    def get_answers(self, query, top_k=3, num_faqs=3, num_questions=10, num_docs=10):
        """
        Return top_k number of Answers based on user query.

        :param query         : User's question/query
        :param top_k         : Number of Answers returned (default is 3)
        :param num_faqs      : Number of retrieved FAQ answers (default is 3)
        :param num_questions : Number of retrieved Questions (default is 10)
        :param num_docs      : Number of retrieved Documents (default is 10)
        :returns answers     : List of Answer objects
        """
        self.query = query
        self.top_k = top_k

        # TODO Try to find answers in FAQ table
        self.faq_answers = self._get_faq_answers(num_faqs)
        # Try to find answers in Questions table
        self.question_answers = self._get_question_answers(num_questions)
        # Try to find answers in Documentation table
        self.doc_answers = self._get_docs_answers(num_docs)

        # sort answers by their `confidence` and select top-k
        self.answers = self.question_answers + self.doc_answers
        self.answers = sorted(self.answers, key=lambda k: k.confidence, reverse=True)
        self.answers = self.answers[:top_k]
        return self.answers
