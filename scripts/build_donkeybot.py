import subprocess
import argparse


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
    detect questions in data_storage
    subprocess.run(
        f"python -m scripts.detect_all_questions", shell=True,
    )
    # create search engine for documents and questions
    subprocess.run(
        f"python -m scripts.create_se_indexes", shell=True,
    )

if __name__ == "__main__":
    main()
