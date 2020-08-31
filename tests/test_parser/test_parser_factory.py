# bot modules
from bot.parser.factory import ParserFactory
from bot.parser.comments import IssueCommentParser
from bot.parser.issues import IssueParser
from bot.parser.docs import RucioDocsParser
from bot.parser.emails import EmailParser

# general python
import pytest


def test_issue_parser_type():
    factory_out = ParserFactory().get_parser("Issue")
    issue_parser = IssueParser()
    assert type(factory_out) == type(issue_parser)


def test_issue_comment_parser_type():
    factory_out = ParserFactory().get_parser("Issue Comment")
    comment_parser = IssueCommentParser()
    assert type(factory_out) == type(comment_parser)


def test_email_parser_type():
    factory_out = ParserFactory().get_parser("Email")
    email_parser = EmailParser()
    assert type(factory_out) == type(email_parser)


def test_rucio_docs_parser_type():
    factory_out = ParserFactory().get_parser("Rucio Documentation")
    rucio_docs_parser = RucioDocsParser()
    assert type(factory_out) == type(rucio_docs_parser)


def test_assertion_stdout_with_str(capfd):
    factory_wrong_int = ParserFactory().get_parser("wrong parser type")
    out, err = capfd.readouterr()
    assert out == "Error: Parser not found.\n"


def test_assertion_stdout_with_int(capfd):
    factory_wrong_int = ParserFactory().get_parser(31415)
    out, err = capfd.readouterr()
    assert out == "Error: Parser not found.\n"
