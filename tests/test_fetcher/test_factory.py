# bot modules
from bot.fetcher.factory import FetcherFactory
from bot.fetcher.docs import RucioDocsFetcher
from bot.fetcher.issues import IssueFetcher

# general python
import pytest


def test_issue_fetcher_type():
    factory_out = FetcherFactory().get_fetcher("Issue")
    assert type(factory_out) == type(IssueFetcher())


def test_rucio_docs_fetcher_type():
    factory_out = FetcherFactory().get_fetcher("Rucio Documentation")
    assert type(factory_out) == type(RucioDocsFetcher())


def test_missing_email_fetcher(capfd):
    factory_wrong_int = FetcherFactory().get_fetcher("Email")
    out, err = capfd.readouterr()
    assert out == "Error: Fetcher not found.\n"


def test_assertion_stdout_with_str(capfd):
    factory_wrong_int = FetcherFactory().get_fetcher("some other string")
    out, err = capfd.readouterr()
    assert out == "Error: Fetcher not found.\n"


def test_assertion_stdout_with_int(capfd):
    factory_wrong_int = FetcherFactory().get_fetcher(31415)
    out, err = capfd.readouterr()
    assert out == "Error: Fetcher not found.\n"
