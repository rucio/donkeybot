# bot modules
from bot.database.sqlite import Database
from bot.parser.emails import EmailParser, Email
import bot.config as config
import bot.utils as utils

# general python
from datetime import datetime
import os
import pytest
import pickle
import hashlib


def teardown_module(module):
    os.remove(config.DATA_DIR + "test_dict.pickle")


@pytest.fixture(scope="module")
def test_db():
    db = Database("test.db", "test_table")
    db.create_emails_table("test_table")
    yield db
    db.close_connection()
    os.remove(config.DATA_DIR + "test.db")


@pytest.fixture(scope="module")
def test_email(test_db):
    email = dict()
    email["sender"] = "<jdoe@gmail.com>"
    email["receiver"] = "<smith@hotmail.com>"
    # choose subject that already exists so that no new cids are created
    email["subject"] = "update to art container"
    email["body"] = "empty body"
    email["date"] = "Wed, 27 Mar 2019 22:11:01 +0100"
    email["db"] = test_db
    email["emails_table_name"] = "test_table"
    yield email


@pytest.fixture(scope="module")
def email_parser(test_email):
    parser = EmailParser()
    yield parser


@pytest.fixture(scope="module")
def parsed_email(test_email, email_parser):
    parsed_email = email_parser.parse(**test_email)
    yield parsed_email


@pytest.fixture(scope="module")
# parsed_email because when we parse -> thats when its inserted into db
def test_email_in_db(parsed_email, test_db):
    the_email_in_the_db = test_db.query(
        "SELECT * \
         FROM test_table\
         WHERE email_id == 1"  # since only 1 email inserted
    )[0]
    yield the_email_in_the_db


def test_email_data_saved_on_db(parsed_email, test_email_in_db):
    # columns fromon .create_emails_table()
    assert test_email_in_db[0] == parsed_email.id  # email_id
    assert test_email_in_db[1] == parsed_email.sender  # sender
    assert test_email_in_db[2] == parsed_email.receiver  # receiver
    assert test_email_in_db[3] == parsed_email.subject  # subject
    assert test_email_in_db[4] == parsed_email.body  # doc_bodytype
    # date must have a specific format and parsed_email.date is datetime obj
    assert test_email_in_db[5] == parsed_email.date.strftime(
        "%Y-%m-%d %H:%M:%S+00:00"
    )  # email_date
    assert test_email_in_db[6] == parsed_email.first_email  # first_email
    assert test_email_in_db[7] == parsed_email.reply_email  # reply_email
    assert test_email_in_db[8] == parsed_email.fwd_email  # fwd_email
    assert test_email_in_db[9] == parsed_email.clean_body  # clean_body
    assert test_email_in_db[10] == parsed_email.conversation_id  # conversation_id


# should this be under sqlite test?
def test_email_types_on_db(test_email_in_db):
    assert type(test_email_in_db[0]) == int  # email_id
    assert type(test_email_in_db[1]) == str  # sender
    assert type(test_email_in_db[2]) == str  # receiver
    assert type(test_email_in_db[3]) == str  # subject
    assert type(test_email_in_db[4]) == str  # doc_bodytype
    assert type(test_email_in_db[5]) == str  # email_date
    assert type(test_email_in_db[6]) == int  # first_email
    assert type(test_email_in_db[7]) == int  # reply_email
    assert type(test_email_in_db[8]) == int  # fwd_email
    assert type(test_email_in_db[9]) == str  # clean_body
    assert type(test_email_in_db[10]) == str  # conversation_id


def test_parsed_email_cls_type(parsed_email):
    assert type(parsed_email) == Email


def test_parsed_email_attribute_types(parsed_email):
    assert type(parsed_email.__dict__) == dict
    assert type(parsed_email.id) == int
    assert type(parsed_email.sender) == str
    assert type(parsed_email.receiver) == str
    assert type(parsed_email.subject) == str
    assert type(parsed_email.body) == str
    assert type(parsed_email.date) == datetime
    assert type(parsed_email.first_email) == int
    assert type(parsed_email.reply_email) == int
    assert type(parsed_email.fwd_email) == int
    assert type(parsed_email.clean_body) == str
    assert type(parsed_email.conversation_id) == str


def test_parsed_email_id(parsed_email):
    assert (
        parsed_email.id == 1
    )  # only one email exists in the test_db (the test_email from the fixture)


def test_email_id_increase(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    parsed_other_test_email = email_parser.parse(**other_test_email)
    assert parsed_other_test_email.id == 2  # id should have increased


def test_parsed_email_sender(parsed_email):
    assert parsed_email.sender == "jdoe@gmail.com"


def test_multiple_senders_error(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    other_test_email["sender"] = "<jdoe@gmail.com>, <will@live.com>"
    with pytest.raises(
        SystemExit
    ):  # raises SystemExit because of sys.exit(MultipleSendersError)
        parsed_other_test_email = email_parser.parse(**other_test_email)


def test_parsed_email_receiver(parsed_email):
    assert parsed_email.receiver == "smith@hotmail.com"


def test_multiple_receivers_in_csv(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    other_test_email["receiver"] = "<smith@hotmail.com>, <will@live.com>"
    parsed_other_test_email = email_parser.parse(**other_test_email)
    assert parsed_other_test_email.receiver == "smith@hotmail.com, will@live.com"


def test_parsed_email_subject(parsed_email):
    assert parsed_email.subject == "update to art container"


def test_find_conversation_hashing(test_email, email_parser):
    find_conversation_hash = email_parser.find_conversation(test_email["subject"])
    clean_subject = email_parser.clean_subject(test_email["subject"])
    update_to_art_contained_cid = (
        "cid_" + hashlib.md5(clean_subject.encode("utf-8")).hexdigest()[:6]
    )
    assert find_conversation_hash == update_to_art_contained_cid


def test_parsed_email_conversation_id(test_email, parsed_email, email_parser):
    find_conversation_hash = email_parser.find_conversation(test_email["subject"])
    assert parsed_email.conversation_id == find_conversation_hash


def test_cid_not_created_for_first_email(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    other_test_email[
        "subject"
    ] = "first email subject where a conv id should not be created or exist"
    find_conversation_hash = email_parser.find_conversation(
        other_test_email["subject"], dict_name="test_dict"
    )
    # make sure hash not found
    assert find_conversation_hash == None


def test_cid_not_created_for_fwd_email(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    other_test_email[
        "subject"
    ] = "FWD: fwd email subject where a conv id should not be created or exist"
    find_conversation_hash = email_parser.find_conversation(
        other_test_email["subject"], dict_name="test_dict"
    )
    # make sure hash not found
    assert find_conversation_hash == None


def test_cid_created_for_re_email(test_email, email_parser):
    other_test_email = {k: v for k, v in test_email.items()}
    other_test_email["subject"] = "RE: reply email where con id should be created"
    find_conversation_hash = email_parser.find_conversation(
        other_test_email["subject"], dict_name="test_dict"
    )
    # make sure hash was created
    assert find_conversation_hash != None
    # make sure it was saved in the test conversation dict
    with open(config.DATA_DIR + "test_dict.pickle", "rb") as f:
        test_conv_dict = pickle.load(f)
    assert find_conversation_hash in test_conv_dict.values()


def test_parsed_email_category(parsed_email):
    assert parsed_email.first_email == 1
    assert parsed_email.reply_email == 0
    assert parsed_email.fwd_email == 0


def test_parsed_email_body(test_email, parsed_email):
    assert parsed_email.body == test_email["body"]
    assert parsed_email.clean_body == test_email["body"]


def test_parsed_email_date(test_email, parsed_email):
    # '%a, %d %b %Y %H:%M:%S %z' is the date format we find in Rucio Emails
    assert parsed_email.date == utils.convert_to_utc(
        test_email["date"], "%a, %d %b %Y %H:%M:%S %z"
    )


def test_clean_body_fix_url(email_parser):
    body = "https://github\n.com/rucio/donkeybo\nt"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "https://github.com/rucio/donkeybot"


def test_clean_body_no_newline(email_parser):
    body = "Text \nwith \nnewline \ncharacters"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "Text with newline characters"


def test_clean_body_ON_HDR_REGEX(email_parser):
    body = "correct text On 20/20/2020 wrote: you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_ORIGINAL_MSG_REGEX(email_parser):
    body = "correct text -----Original Message----- you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_QUOTED_REGEX(email_parser):
    body = "correct text >> you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_QUOTED_REGEX_2(email_parser):
    body = "correct text > > you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_QUOTED_REGEX_3(email_parser):
    body = "correct text >>>> > you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_HEADER_REGEX(email_parser):
    body = "correct text ________ From: Vasilis Sent: Hello To: You Subject: Developer you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_body_HEADER_REGEX_2(email_parser):
    body = "correct text  From: Vasilis Sent: Hello To: You Subject: Developer you should not see this"
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text"


def test_clean_body_stops_at_first_regex(email_parser):
    body = (
        "correct text >>>>  you should not see this -----Original Message----- or this"
    )
    cleaned_body = email_parser.clean_body(body)
    assert cleaned_body == "correct text "


def test_clean_subject_fwd(email_parser):
    subject = "FWD: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_fwd_2(email_parser):
    subject = "FwD: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_fwd_3(email_parser):
    subject = "Fwd: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_re(email_parser):
    subject = "RE: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_re_2(email_parser):
    subject = "re: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_re_3(email_parser):
    subject = "Re: something"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "something"


def test_clean_subject_REGEX_METACHARACTERS(email_parser):
    subject = "^$.|?*+(){}[]Hey"
    cleaned_body = email_parser.clean_subject(subject)
    assert cleaned_body == "hey"
