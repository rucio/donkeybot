# bot modules
from bot.parser.interface import IParser


def test_method_existences():
    assert "parse_dataframe" in (IParser.__abstractmethods__)
    assert "parse" in (IParser.__abstractmethods__)
