# general python
from uuid import uuid4
import datetime


class FAQ:
    def __init__(
        self,
        question,
        answer,
        author,
        keywords,
    ):
        # Set unique ID
        self.faq_id = "faq_" + str(uuid4().hex)
        self.question = question
        self.answer = answer
        self.author = author
        self.keywords = keywords
        # +00:00 since its utcnow() + same format as other dates saved in data_storage
        self.created_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S+00:00")

    def __str__(self):
        return (
            f"question: {self.question}\n answer: {self.answer}\n author: {self.author}"
        )
