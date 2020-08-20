# This script :
# 1) Fetches GitHub Rucio issues and Documentation and saves them under
#     -  '/data/issues_input_data.db'
#     -  '/data/docs_input_data.db'
# 2) Parses the above .db files + the emails_input_data.db file
#     - expects '/data/emails_input_data.db' to exist
#       (not fetched automatically as of 18/08/2020)
# 3) Detects questions in issues/issue_comments/emails
# 4) Creates rucio documentation and questions indexes for the SearchEngine
# 5) Saves all of the above under '/data/data_storage.db'

#bot modules
import bot.config as config

# general python
import subprocess
import argparse
import os


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""Use this script to build DonkeyBot"""
    )
    required = parser.add_argument_group("required arguments")

    required.add_argument(
        "-t",
        "--token",
        help="GitHub api token to be used for the GET requests while fetching",
        required=True,
    )

    args = parser.parse_args()
    api_token = args.token

    # # fetch and store data
    # subprocess.run(
    #     f"python -m scripts.fetch_issues -r rucio/rucio -t {api_token}", shell=True,
    # )
    # subprocess.run(
    #     f"python -m scripts.fetch_rucio_docs -t {api_token}", shell=True,
    # )
    # # parse and store data
    # subprocess.run(
    #     f"python -m scripts.parse_all", shell=True,
    # )
    # # detect questions in data_storage
    # subprocess.run(
    #     f"python -m scripts.detect_all_questions", shell=True,
    # )
    # create search engine for documents and questions
    subprocess.run(
        f"python -m scripts.create_se_indexes", shell=True,
    )
    # download BERT models for Question Answering
    try:
        os.makedirs(config.DATA_DIR+"models/distilbert-base-cased-distilled-squad")
        os.makedirs(config.DATA_DIR+"models/bert-large-cased-whole-word-masking-finetuned-squad")
        os.makedirs(config.DATA_DIR+"models/bert-large-uncased-whole-word-masking-finetuned-squad")
    except FileExistsError as _e:
        print(_e)
        print('moving on...')

    print('Done!')



if __name__ == "__main__":
    main()
