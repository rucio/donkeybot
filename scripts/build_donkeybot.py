# bot modules
from bot.config import MODELS_DIR, DATA_DIR
from bot.utils import str2bool
from bot.database.sqlite import Database

# general python
import subprocess
import argparse
import os
import json
from transformers import BertForQuestionAnswering, BertTokenizer
from transformers import DistilBertForQuestionAnswering, DistilBertTokenizer


def download_and_save_DistilBERT_model(name):
    """Download and save DistilBERT transformer model to MODELS_DIR"""
    print(f"Downloading: {name}")
    try:
        os.makedirs(MODELS_DIR + f"{name}")
    except FileExistsError as _e:
        pass
    model = DistilBertForQuestionAnswering.from_pretrained(f"{name}")
    tokenizer = DistilBertTokenizer.from_pretrained(f"{name}")
    model.save_pretrained(MODELS_DIR + f"{name}")
    tokenizer.save_pretrained(MODELS_DIR + f"{name}")
    return


def download_and_save_BERT_model(name):
    """Download and save BERT transformer model to MODELS_DIR"""
    print(f"Downloading: {name}")
    try:
        os.makedirs(MODELS_DIR + f"{name}")
    except FileExistsError as _e:
        pass
    model = BertForQuestionAnswering.from_pretrained(f"{name}")
    tokenizer = BertTokenizer.from_pretrained(f"{name}")
    model.save_pretrained(MODELS_DIR + f"{name}")
    tokenizer.save_pretrained(MODELS_DIR + f"{name}")
    return


def fetch_faq_data():
    """Creates FAQ table and populates it with data in faq.json"""
    # create faq table
    print(f"Creating faq table in data_storage.db")
    data_storage = Database("data_storage.db")
    data_storage.create_faq_table()
    # load faq data
    with open(DATA_DIR + "faq.json") as json_file:
        data = json.load(json_file)
    # insert data to db
    print(f"Inserting data from faq.json file...")
    for faq in data:
        data_storage.insert_faq(faq)
    data_storage.close_connection()


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(
        description="""Use this script to build DonkeyBot"""
    )
    required = parser.add_argument_group("required arguments")
    optional = parser.add_argument_group("optional arguments")

    required.add_argument(
        "-t",
        "--token",
        help="GitHub api token to be used for the GET requests while fetching",
        required=True,
    )
    optional.add_argument(
        "-all",
        "--all_models",
        type=str2bool,
        nargs="?",  # 0 or 1 argument,
        const=True,
        default=False,
        help="If True then download all Question Answering models the bot supports. (default is False)",
    )
    optional.add_argument(
        "--include_emails",
        type=str2bool,
        nargs="?",  # 0 or 1 argument,
        const=True,
        default=False,
        help="If True then also parse emails_input_data from /data folder. (default is False)",
    )
    args = parser.parse_args()
    api_token = args.token
    download_all_models = args.all_models
    include_emails = args.include_emails

    # Fetch FAQ data from faq.json
    fetch_faq_data()
    # Fetch and store issues and rucio documentation data
    subprocess.run(
        f"python -m scripts.fetch_issues -r rucio/rucio -t {api_token}",
        shell=True,
    )
    subprocess.run(
        f"python -m scripts.fetch_rucio_docs -t {api_token}",
        shell=True,
    )
    # parse and store data
    subprocess.run(
        f"python -m scripts.parse_issues -i issues_input_data -o data_storage",
        shell=True,
    )
    subprocess.run(
        f"python -m scripts.parse_issue_comments -i issues_input_data -o data_storage",
        shell=True,
    )
    subprocess.run(
        f"python -m scripts.parse_docs -i docs_input_data -o data_storage",
        shell=True,
    )
    if include_emails:  # default is false       
        subprocess.run(
            f"python -m scripts.parse_emails -i emails_input_data -o data_storage",
            shell=True,
        )
    # detect questions in data_storage
    subprocess.run(
        f"python -m scripts.detect_issue_questions -db data_storage --issues_table issues --questions_table questions",
        shell=True,
    )
    subprocess.run(
        f"python -m scripts.detect_comment_questions -db data_storage --comments_table issue_comments --questions_table questions",
        shell=True,
    )
    if include_emails: # default is false       
        subprocess.run(
            f"python -m scripts.detect_email_questions -db data_storage --emails_table emails --questions_table questions",
            shell=True,
        )
    # create search engine for documents questions and faq
    subprocess.run(
        f"python -m scripts.create_se_indexes",
        shell=True,
    )
    # download and cache Question Answering models
    download_and_save_DistilBERT_model("distilbert-base-cased-distilled-squad")
    if download_all_models:
        download_and_save_DistilBERT_model("distilbert-base-uncased-distilled-squad")
        download_and_save_BERT_model(
            "bert-large-cased-whole-word-masking-finetuned-squad"
        )
        download_and_save_BERT_model(
            "bert-large-uncased-whole-word-masking-finetuned-squad"
        )
    print("Done!")


if __name__ == "__main__":
    main()
