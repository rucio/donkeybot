# bot modules
import bot.utils as utils
import bot.config as config
from bot.database.sqlite import Database
from bot.fetcher.interface import IFetcher, LoadingError, SavingError, InvalidTokenError

# general python
import string
import re
import pandas as pd
import numpy as np
from tqdm import tqdm
import sys
import requests


class RucioDocsFetcher(IFetcher):
    """Fetcher for Rucio's documentation in GitHub."""

    def __init__(self):
        self.type = "Rucio Documentation Fetcher"
        self.repo = "rucio/rucio"
        self.docs_url = f"https://api.github.com/repos/{self.repo}/contents/doc/source"
        # root_download_url + filepath gives us the raw form of the data in a file
        # eg. root_download_url + '/doc/source/man/daemons.rst'
        self.root_download_url = "https://raw.githubusercontent.com/rucio/rucio/master"
        return

    def _check_token(self):
        """Check the GitHub token's validity."""
        try:
            ##TODO improve hacky approach below
            # if the request is correct then no message is returned and we have a TypeError
            if (
                utils.request(self.docs_url, self.headers)["message"]
                == "Bad credentials"
            ):
                raise InvalidTokenError(
                    f"\nError: Bad credentials. The OAUTH token {self.api_token} is not correct."
                )
        except InvalidTokenError as _e:
            sys.exit(_e)
        except:
            # we don't care about the TypeError
            pass

    def _extract_daemon_body(self, body):
        """
        Parses the body of the daemon documentation under 'doc/source/man/'.

        1) finds patterns like
                .. argparse::
                :filename: bin/rucio-bb8
                :func: get_parser
                :prog: rucio-bb8

        2) Then moves on to the appropriate path and matches two regex patterns
            2.1) One that matches the description content for each daemon
            2.2) One the epilog content for each daemon
                (more info under bot.config.py)

        If the first pattern doesn't match we simply return the initial body.

        : param body        : initial, raw daemon documentation body under doc/source/man/
        : return final_body : final daemon documentation body including the docstrings
        """
        # try and match the first pattern
        if config.DAEMON_DOC_ARGS_REGEX.search(body) is not None:
            for match in config.DAEMON_DOC_ARGS_REGEX.finditer(body):
                daemon_filename = match.group(1)
                # daemon_func = match.group(2) and daemon_prog = match.group(3) unused variables for now
                start_idx = match.start()
                end_idx = match.end()
            # construct the download url for the raw body of each daemon
            daemon_code_url = self.root_download_url + f"/{daemon_filename}"
            daemon_code = requests.get(daemon_code_url).content.decode("utf-8")

            # try to match the 2 other regexes that extract the docstring
            full_matches = ""
            if config.DAEMON_DESC_REGEX.search(daemon_code) is not None:
                for match in config.DAEMON_DESC_REGEX.finditer(daemon_code):
                    description_match = match.group(1)
                    description_match = description_match[1:-1]
                    full_matches = full_matches + description_match
            if config.DAEMON_EPILOG_REGEX.search(daemon_code) is not None:
                for match in config.DAEMON_EPILOG_REGEX.finditer(daemon_code):
                    epilog_match = match.group(1)
                    full_matches = full_matches + epilog_match
            final_body = body[:start_idx] + full_matches + body[end_idx:]
            return final_body
        else:
            return body

    def fetch(self, api_token):
        """
        Returns a pandas DataFrames that holds information for
        Rucio's documentation, utilizing GitHub's api.

        attributes:
            doc_id   : doc's id
            name     : doc's name/title
            url      : doc's url
            body     : doc's creator
            doc_type : 'general', 'daemon' or 'release_notes'

        :param api_token : GitHub api token used for fetching the data
        :return docs_df  : DataFrame containing all the information for Rucio's docs
        """
        self.api_token = api_token
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"token {self.api_token}",
        }
        self._check_token()

        docs_df = pd.DataFrame(columns=["doc_id", "name", "url", "body", "doc_type"])

        doc_id = 0
        print("Fetching Rucio documentation...")
        for doc in tqdm(utils.request(self.docs_url, self.headers)):
            if type(doc) == str:
                print(f"Error: Problem fetching the doc {doc} moving on to the next...")
                continue
            elif doc["type"] == "file":
                if doc["name"].split(".")[-1] not in ["rst", "md"]:
                    continue
                doc_name = doc["name"]
                doc_url = doc["html_url"]
                doc_download_url = doc["download_url"]
                doc_body = requests.get(doc_download_url).content.decode("utf-8")
                docs_df = docs_df.append(
                    {
                        "doc_id": doc_id,
                        "name": doc_name,
                        "url": doc_url,
                        "body": doc_body,
                        "doc_type": "general",
                    },
                    ignore_index=True,
                )
                doc_id += 1
            elif doc["type"] == "dir":
                if doc["name"] == "images":
                    pass
                # daemon documentation exists under the man directory
                elif doc["name"] == "man":
                    print("\nFetching the daemon documentation...")
                    man_url = doc["url"]
                    try:
                        daemons_url = (
                            self.root_download_url + "/doc/source/man/daemons.rst"
                        )
                        daemon_body = requests.get(daemons_url).content.decode("utf-8")
                        # regex used to extract daemon names from body
                        daemons = re.findall("rucio-.*$", daemon_body, re.MULTILINE)
                    except:
                        raise AssertionError(
                            "There is a problem with the daemons_url. Double check if it has changed"
                        )
                    for man_doc in utils.request(man_url, self.headers):
                        if type(man_doc) == str:
                            print(
                                f"Error : There was a problem fetching the file : {man_doc}"
                            )
                            continue
                        elif man_doc["name"].split(".")[-1] not in ["rst", "md"]:
                            continue
                        else:
                            # make sure that we are looking at daemon documentation
                            if man_doc["name"].split(".")[0] in daemons:
                                doc_name = man_doc["name"]
                                doc_url = man_doc["html_url"]
                                doc_download_url = man_doc["download_url"]
                                # In Rucio daemons the doc_body usually points to the docsting documentation
                                doc_body = requests.get(
                                    doc_download_url
                                ).content.decode("utf-8")
                                # We need additional handling to get it, done with _extract_daemon_body method
                                final_doc_body = self._extract_daemon_body(doc_body)
                                docs_df = docs_df.append(
                                    {
                                        "doc_id": doc_id,
                                        "name": doc_name,
                                        "url": doc_url,
                                        "body": final_doc_body,
                                        "doc_type": "daemon",
                                    },
                                    ignore_index=True,
                                )
                                doc_id += 1
                elif doc["name"] == "releasenotes":
                    print("\nFetching the release notes...")
                    release_notes_url = doc["url"]
                    for release_note in utils.request(release_notes_url, self.headers):
                        if type(release_note) == str:
                            print(
                                f"Error: Problem fetching the release note {release_note}"
                            )
                            continue
                        elif release_note["name"].split(".")[-1] not in ["rst", "md"]:
                            continue
                        else:
                            doc_name = release_note["name"]
                            doc_url = release_note["html_url"]
                            doc_download_url = release_note["download_url"]
                            doc_body = requests.get(doc_download_url).content.decode(
                                "utf-8"
                            )
                            docs_df = docs_df.append(
                                {
                                    "doc_id": doc_id,
                                    "name": doc_name,
                                    "url": doc_url,
                                    "body": doc_body,
                                    "doc_type": "release_notes",
                                },
                                ignore_index=True,
                            )
                            doc_id += 1
                ##TODO handle restapi, api
                # Below are complicated for now, if we want to integrate we can
                # download and compile with Sphinx the Makefile etc
                # restapi documentation
                elif doc["name"] == "restapi":
                    pass
                # api documentation
                elif doc["name"] == "api":
                    pass
        self.docs = docs_df
        return docs_df

    def save(self, db=Database, docs_table_name="docs"):
        """
        Save the data in a .db file utilizing our sqlite wrapper

        : param db                 : bot.database.sqlite Database object
        : param  docs_table_name   : name of the table where we'll store the docs
        """
        if hasattr(self, "docs"):
            print("Saving...")
            self.docs.to_sql(
                docs_table_name, con=db.db, if_exists="replace", index=False
            )
        else:
            raise SavingError(
                f"\nError: We are missing the data. Please use the .fetch() method before saving."
            )

    def load(self, db=Database, docs_table_name="docs"):
        """
        Load the data from the .db file.

        : param  db                  : bot.database.sqlite Database object
        : param  docs_table_name     : name of the table where we'll store the docs
        : return docs                : DataFrame holding the documentation data
        """
        try:
            print("Loading...")
            self.docs = db.get_dataframe(f"{docs_table_name}")
            return self.docs
        except:
            raise LoadingError(f"\nError: Data not found.")
