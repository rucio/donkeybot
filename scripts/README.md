# inputs

This code is used to get the email data using IMAP and then apply the [Name Tagger](../docs/name_tagger.md) to keep everything private. The output of these scripts is the initial input the bot creation. For more information look at the [documentation](../docs/approach.md).


# dataset_creation.py

This script is responsible for most of phase 1 in the bot's creation process. 
To read more about said process and our approach you can read the [documentation](../docs/approach.md).



# fetch_issues.py

This script is used when fetching GitHub issues and comments from a specific repo.
Simply run :  

``` bash
python fetch_issues --repo <repository> --token <your_api_token>
```
eg.
`python fetch_issues -r rucio/rucio -token <my_token>` 
will fetch all the issues and comments under [rucio/rucio](https://github.com/rucio/rucio/issues).

other optional arguments:
- --database       : Output .db file where the data is stored (default is dataset)
- --max_pages      : Maximum number of pages we will request through GitHubs api (default is 201)
- --issues_table   : Name of the table where we will store the issues (default is issues)
- --comments_table : Name of the table where we will store the comments (default is issue_comments)