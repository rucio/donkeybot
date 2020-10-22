import os.path
from pathlib import Path
import re

# PATHS
TOP_LEVEL_DIR = str(Path(__file__).parents[2]) 
DATA_DIR = os.path.join(TOP_LEVEL_DIR, "data/")
MODELS_DIR = os.path.join(TOP_LEVEL_DIR, "models/")

# REGEX
REGEX_METACHARACTERS = "^$.|?*+(){}[]"
# (EmailParser)
ON_HDR_REGEX = re.compile(r"On (.*?)wrote: ", re.IGNORECASE)
QUOTED_REGEX = re.compile(r"(>>+|> >+)")
HEADER_REGEX = re.compile(
    r"(([_-]{7,})?(\s)From:(.*)(Sent:)?(.*)To:(.*)Subject:)", re.IGNORECASE
)
ORIGINAL_MSG_REGEX = re.compile(r"-----Original Message-----", re.IGNORECASE)
# (RucioDocsFetcher)
DAEMON_DOC_ARGS_REGEX = re.compile(
    r"..\sargparse::[\n\r\s]+:filename:\s(.*)[\n\r\s]+:func:\s(.*)[\n\r\s]+:prog:\s(.*)"
)
# matches any string after inside ArgumentParser description for both types of quotes
DAEMON_DESC_REGEX = re.compile(
    r"""ArgumentParser\(description=(?:("[^"]*"|'[^']*'))""", re.DOTALL
)
# matches the text inside epilog (which is in ArgumentParser) for both types of quotes
DAEMON_EPILOG_REGEX = re.compile(r"""epilog=['|"]{3}(.*)['|"]{3}""", re.DOTALL)
# (Other)
URL_REGEX = re.compile(r"(https|http|www)[^ ]*")
USER_MENTION_REGEX = re.compile(r"@[^\s]*")
