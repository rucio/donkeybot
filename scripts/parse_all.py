import subprocess
import argparse


def main():
    # Parse cli arguments
    parser = argparse.ArgumentParser(description='''This is the script responsible for parsing all data''')
    optional = parser.add_argument_group('optional arguments')
    
    optional.add_argument(
        '--emails_input_db',
        default='emails_noNER_22062020',
        help='Input .db file name of the fetched emails (default is emails_noNER_22062020)')
    optional.add_argument(
        '--issues_input_db',
        default='issues_input_data',
        help='Input .db file name of the fetched issues (default is issues_input_data)')
    optional.add_argument(
        '--docs_input_db',
        default='docs_input_data',
        help='Input .db file name of the fetched documentation (default is docs_input_data)')
    optional.add_argument(
        '-o',
        '--output_db',
        default='data_storage',
        help='Output .db file name of the parsed data (default is data_storage)')

    args            = parser.parse_args()
    emails_input_db = args.emails_input_db
    issues_input_db = args.issues_input_db
    docs_input_db   = args.docs_input_db
    output_db       = args.output_db

    # run parsing scripts
    subprocess.run(f'python -m scripts.parse_issues         -i {issues_input_db} -o {output_db}', shell=True)
    subprocess.run(f'python -m scripts.parse_issue_comments -i {issues_input_db} -o {output_db}', shell=True)
    subprocess.run(f'python -m scripts.parse_emails         -i {emails_input_db} -o {output_db}', shell=True)
    subprocess.run(f'python -m scripts.parse_docs           -i {docs_input_db}   -o {output_db}', shell=True)


if __name__ == '__main__':
    main()