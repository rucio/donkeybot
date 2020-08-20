# This script :
# - expects '/data/emails_input_data.db' to exist

# bot modules
from bot.config import MODELS_DIR
from bot.utils import str2bool

# general python
import subprocess
import argparse
import os
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
        help="If True then download all Question Answering models the bot supports. (default it False)",
        
    )

    args = parser.parse_args()
    api_token = args.token
    download_all_models = args.all_models

    # fetch and store data
    subprocess.run(
        f"python -m scripts.fetch_issues -r rucio/rucio -t {api_token}", shell=True,
    )
    subprocess.run(
        f"python -m scripts.fetch_rucio_docs -t {api_token}", shell=True,
    )
    # parse and store data
    subprocess.run(
        f"python -m scripts.parse_all", shell=True,
    )
    # detect questions in data_storage
    subprocess.run(
        f"python -m scripts.detect_all_questions", shell=True,
    )
    # create search engine for documents and questions
    subprocess.run(
        f"python -m scripts.create_se_indexes", shell=True,
    )
    # download and cache Question Answering models
    download_and_save_DistilBERT_model("distilbert-base-uncased-distilled-squad")
    if download_all_models:
        download_and_save_DistilBERT_model("distilbert-base-cased-distilled-squad")
        download_and_save_BERT_model("bert-large-cased-whole-word-masking-finetuned-squad")
        download_and_save_BERT_model("bert-large-uncased-whole-word-masking-finetuned-squad")
    print("Done!")


if __name__ == "__main__":
    main()
