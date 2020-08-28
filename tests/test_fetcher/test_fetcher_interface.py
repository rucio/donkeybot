# bot modules
from bot.fetcher.interface import IFetcher


def test_method_existences():
    assert "fetch" in (IFetcher.__abstractmethods__)
    assert "save" in (IFetcher.__abstractmethods__)
    assert "load" in (IFetcher.__abstractmethods__)
