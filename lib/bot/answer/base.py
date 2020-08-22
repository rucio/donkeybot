# general python
from uuid import uuid4
import datetime
import hashlib
import re


class Answer:
    def __init__(
        self,
        question,
        answer,
        model,
        start,
        end,
        confidence,
        extended_answer,
        extended_start,
        extended_end,
        metadata,
    ):
        # Set unique ID
        self.id = str(uuid4().hex)
        self.user_question = question
        # Since multiple answers can be created for the same user_question
        # Let's create an id for the user_question
        clean_question = str(question).lower()
        # disregard all trailing question marks and spaces from the hashing
        if clean_question[-1] == "?":
            clean_question = re.sub("[ ?]*$", "", clean_question)
        self.user_question_id = hashlib.md5(clean_question.encode("utf-8")).hexdigest()[
            :10
        ]
        self.answer = answer
        self.start = start
        self.end = end
        self.confidence = confidence
        self.extended_answer = extended_answer
        self.extended_start = extended_start
        self.extended_end = extended_end
        self.model = model
        # TODO add FAQ option as an origin
        if "doc_id" in metadata:
            self.origin = "documentation"
        elif "faq_id" in metadata:
            self.origin = "faq"
        else:
            self.origin = "questions"
        # +00:00 since its utcnow() + same format as other dates saved in data_storage
        self.created_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S+00:00")
        self.label = None
        self.metadata = metadata

    def __str__(self):
        return f"answer: {self.extended_answer}... , confidence: {self.confidence}''"
