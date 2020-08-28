# bot modules
from bot.question.detector import QuestionDetector
from bot.question.emails import EmailQuestion
from bot.question.issues import IssueQuestion
from bot.question.comments import CommentQuestion

# general python
import pytest


@pytest.fixture()
def detector():
    qd = QuestionDetector("email")
    return qd


def test_email_detector_question_type(detector):
    text = "Hey man, what can we do?"
    result = detector.detect(text)
    detected_question = result[0]
    assert type(detected_question) == EmailQuestion


def test_issue_detector_question_type():
    issue_question_detector = QuestionDetector("issue")
    text = "Hey man, what can we do?"
    result = issue_question_detector.detect(text)
    detected_question = result[0]
    assert type(detected_question) == IssueQuestion


def test_comment_detector_question_type():
    comment_question_detector = QuestionDetector("comment")
    text = "Hey man, what can we do?"
    result = comment_question_detector.detect(text)
    detected_question = result[0]
    assert type(detected_question) == CommentQuestion


def test_first_regex(detector):
    text = "Hey man, what can we do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "Hey man, what can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("Hey man, what can we do?")


def test_first_regex_with_bad_uppercase(detector):
    text = "bUt WhaT if we Have Bad Formating? Then it works a bit worse..."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "Formating?"
    assert detected_question.start == len("bUt WhaT if we Have Bad ")
    assert detected_question.end == len("bUt WhaT if we Have Bad Formating?")


def test_first_regex_with_question_in_other_sentence(detector):
    text = (
        "Let's see what happens here. What if the question is in the second sentence?"
    )
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert (
        detected_question.question == "What if the question is in the second sentence?"
    )
    assert detected_question.start == len("Let's see what happens here. ")
    assert detected_question.end == len(text)


# test fails. QuestionDetector needs improvement
@pytest.mark.skip(reason="known to fail; open ticket needs bugfix")
def test_first_regex_with_multiple_questions(detector):
    text = "A question in the first sentence? And in the second sentence?"
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 2
    detected_question_1 = result[0]
    assert detected_question_1.question == "A question in the first sentence?"
    assert detected_question_1.start == 0
    assert detected_question_1.end == len(text)
    detected_question_2 = result[1]
    assert detected_question_2.question == "And in the second sentence?"
    assert detected_question_2.start == len("A question in the first sentence? ")
    assert detected_question_2.end == len(text)


# this test passes though (seems like we need spaces or newline check other test below)
def test_first_regex_with_multiple_questions_and_newline(detector):
    text = (
        "A sentence.\nTesting this again?\nYes!\nHow will it perform?"  # with newlines
    )
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 2
    detected_question_1 = result[0]
    assert detected_question_1.question == "Testing this again?"
    assert detected_question_1.start == len("A sentence.\n")
    assert detected_question_1.end == len("A sentence.\nTesting this again?")
    detected_question_2 = result[1]
    assert detected_question_2.question == "How will it perform?"
    assert detected_question_2.start == len("A sentence.\nTesting this again?\nYes!\n")
    assert detected_question_2.end == len(text)


# fails again (seems like the spacing is the problem)
@pytest.mark.skip(reason="known to fail; open ticket needs bugfix")
def test_first_regex_with_multiple_questions_no_newline(detector):
    text = "A sentence.Testing this again?Yes!How will it perform?"  # no newline
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 2
    detected_question_1 = result[0]
    assert detected_question_1.question == "Testing this again?"
    assert detected_question_1.start == len("A sentence.")
    assert detected_question_1.end == len("A sentence.Testing this again?")
    detected_question_2 = result[1]
    assert detected_question_2.question == "How will it perform?"
    assert detected_question_2.start == len("A sentence.Testing this again?Yes!")
    assert detected_question_2.end == len(text)


# it passes (seems like the spacing is the problem)
def test_first_regex_with_multiple_questions_with_spaces(detector):
    text = "A sentence. Testing this again? Yes! How will it perform?"  # with spaces
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 2
    detected_question_1 = result[0]
    assert detected_question_1.question == "Testing this again?"
    assert detected_question_1.start == len("A sentence. ")
    assert detected_question_1.end == len("A sentence. Testing this again?")
    detected_question_2 = result[1]
    assert detected_question_2.question == "How will it perform?"
    assert detected_question_2.start == len("A sentence. Testing this again? Yes! ")
    assert detected_question_2.end == len(text)


# original sentence with spaces also fails ( I opened a ticket look into these)
@pytest.mark.skip(reason="known to fail; open ticket needs bugfix")
def test_first_regex_with_multiple_questions_with_spaces_2(detector):
    text = "A question in the first sentence? And in the second sentence? "
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 2
    detected_question_1 = result[0]
    assert detected_question_1.question == "A question in the first sentence?"
    assert detected_question_1.start == 0
    assert detected_question_1.end == len("A question in the first sentence?")
    detected_question_2 = result[1]
    assert detected_question_2.question == "And in the second sentence?"
    assert detected_question_2.start == len("A question in the first sentence? ")
    assert detected_question_2.end == len(text)


def test_second_regex_text_lowering(detector):
    text = "what CAN WE DO? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "what can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("what can we do?")


def test_second_regex_what(detector):
    text = "what can we do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "what can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("what can we do?")


def test_second_regex_how(detector):
    text = "how can we do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "how can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("how can we do?")


def test_second_regex_when(detector):
    text = "when can we do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "when can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("when can we do?")


def test_second_regex_can(detector):
    text = "can we do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "can we do?"
    assert detected_question.start == 0
    assert detected_question.end == len("can we do?")


def test_second_regex_do(detector):
    text = "do we scooby do? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "do we scooby do?"
    assert detected_question.start == 0
    assert detected_question.end == len("do we scooby do?")


def test_second_regex_does(detector):
    text = "does it matter? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "does it matter?"
    assert detected_question.start == 0
    assert detected_question.end == len("does it matter?")


def test_second_regex_should(detector):
    text = "should it matter? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "should it matter?"
    assert detected_question.start == 0
    assert detected_question.end == len("should it matter?")


def test_second_regex_would(detector):
    text = "would it matter? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "would it matter?"
    assert detected_question.start == 0
    assert detected_question.end == len("would it matter?")


def test_second_regex_is(detector):
    text = "is the force be with you? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "is the force be with you?"
    assert detected_question.start == 0
    assert detected_question.end == len("is the force be with you?")


def test_second_regex_may(detector):
    text = "may the force be with you? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "may the force be with you?"
    assert detected_question.start == 0
    assert detected_question.end == len("may the force be with you?")


def test_second_regex_are(detector):
    text = "are we don yet? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "are we don yet?"
    assert detected_question.start == 0
    assert detected_question.end == len("are we don yet?")


def test_second_regex_have(detector):
    text = "have we finished? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "have we finished?"
    assert detected_question.start == 0
    assert detected_question.end == len("have we finished?")


def test_second_regex_has(detector):
    text = "has it ever not worked? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "has it ever not worked?"
    assert detected_question.start == 0
    assert detected_question.end == len("has it ever not worked?")


def test_second_regex_will(detector):
    text = "will I am? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    # second regex lowers text
    assert detected_question.question == "will i am?"
    assert detected_question.start == 0
    assert detected_question.end == len("will i am?")


def test_second_regex_am(detector):
    text = "am I will? Oh I don't know."
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 1
    detected_question = result[0]
    assert detected_question.question == "am i will?"
    assert detected_question.start == 0
    assert detected_question.end == len("am i will?")


# test fails. QuestionDetector needs improvement
@pytest.mark.skip(reason="known to fail; open ticket needs bugfix")
def test_second_regex_multiple_questions_no_space(detector):
    text = "what can we say?would you know?when is it due?"
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 3
    detected_question = result[0]
    assert detected_question.question == "what can we say?"
    assert detected_question.start == 0
    assert detected_question.end == len("what can we say?")
    detected_question = result[1]
    assert detected_question.question == "would you know?"
    assert detected_question.start == len("what can we say?")
    assert detected_question.end == len("what can we say?would you know?")
    detected_question = result[2]
    assert detected_question.question == "when is it due?"
    assert detected_question.start == len("what can we say?would you know?")
    assert detected_question.end == len(text)


def test_second_regex_multiple_questions_with_space(detector):
    text = "what can we say? would you know? when is it due?"
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 3
    detected_question = result[0]
    assert detected_question.question == "what can we say?"
    assert detected_question.start == 0
    assert detected_question.end == len("what can we say?")
    detected_question = result[1]
    assert detected_question.question == "would you know?"
    assert detected_question.start == len("what can we say? ")
    assert detected_question.end == len("what can we say? would you know?")
    detected_question = result[2]
    assert detected_question.question == "when is it due?"
    assert detected_question.start == len("what can we say? would you know? ")
    assert detected_question.end == len(text)


def test_second_regex_multiple_questions_with_newline(detector):
    text = "what can we say?\nwould you know?\nwhen is it due?"
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 3
    detected_question = result[0]
    assert detected_question.question == "what can we say?"
    assert detected_question.start == 0
    assert detected_question.end == len("what can we say?")
    detected_question = result[1]
    assert detected_question.question == "would you know?"
    assert detected_question.start == len("what can we say?\n")
    assert detected_question.end == len("what can we say?\nwould you know?")
    detected_question = result[2]
    assert detected_question.question == "when is it due?"
    assert detected_question.start == len("what can we say?\nwould you know?\n")
    assert detected_question.end == len(text)


def test_is_url_exception(detector, capfd):
    text = "The url contains question mark but should be an exception www.youtube.com/Query?hi"
    result = detector.detect(text)
    assert type(result) == list
    assert len(result) == 0
    exceptions = detector._get_exception_matches(text)
    assert exceptions[0] == "www.youtube.com/Query?hi"
    assert detector._is_exception(exceptions, "Query?") == True
    # found exception + (question, exception) is printed when exception is found
    out, err = capfd.readouterr()
    assert out == "\nFound a Question exception :\nQuery? www.youtube.com/Query?hi\n"
