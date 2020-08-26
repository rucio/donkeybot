[Move back to documentation homepage](https://github.com/rucio/donkeybot/tree/master/docs)

## Contents
- [Contents](#contents)
- [Outline](#outline)
- [How can I use the Question Detector?](#how-can-i-use-the-question-detector)
  - [How can I create a `QuestionDetector`?](#how-can-i-create-a-questiondetector)
  - [So how does the QuestionDetector work?](#so-how-does-the-questiondetector-work)
  - [What is the difference between `IssueQuestion` vs `EmailQuestion` vs `IssueCommentQuestion`?](#what-is-the-difference-between-issuequestion-vs-emailquestion-vs-issuecommentquestion)
  - [What is this `context` attribute I'm seeing in the Question objects?](#what-is-this-context-attribute-im-seeing-in-the-question-objects)
  - [Can I use the QuestionDetector for my projects that aren't issue/email/comment related?](#can-i-use-the-questiondetector-for-my-projects-that-arent-issueemailcomment-related)
- [How can I use the Fetchers?](#how-can-i-use-the-fetchers)
  - [How can I create a `Fetcher` ?](#how-can-i-create-a-fetcher-)
  - [How can I fetch GitHub issues?](#how-can-i-fetch-github-issues)
  - [How does Donkeybot Fetch Rucio Documentation?](#how-does-donkeybot-fetch-rucio-documentation)
  - [How does Donkeybot save the fetched data?](#how-does-donkeybot-save-the-fetched-data)
- [What about the workings of the Search Engines?](#what-about-the-workings-of-the-search-engines)
  - [How can I create a Search Engine?](#how-can-i-create-a-search-engine)
  - [How can I query the Search Engine?](#how-can-i-query-the-search-engine)

## Outline

Almost everything in the sections of this page have a corresponding notebook.  
See [examples](https://github.com/rucio/donkeybot/tree/master/examples) for a more hands on guide by looking at the notebooks.

Also, the functionality explained here is what runs 'under the hood' in the [scripts](https://github.com/rucio/donkeybot/tree/master/scripts) which use Donkeybot.   
So instead of explaining those I chose a more straightforward approach and look at the code with easy examples.

## How can I use the Question Detector?

### How can I create a `QuestionDetector`?

Donkeybot's `QuestionDetector` must be one of the following types : "email", "issue" or "comment"  
This is so that the `QuestionDetector` creates the correct type of Question objects.  
Be it an `EmailQuestion`, `IssueQuestion`, `CommentQuestion`.  

Let's create one for `IssueQuestions`!


```python
from bot.question.detector import QuestionDetector
```


```python
detector = QuestionDetector("issue")
```


```python
text =  """
        What is this 'text', you ask? 
        Well, it's a monologue I'm having... can it help with something you still ask? 
        In testing the QuesitonDetector of course! 
        Did that answer all your questions?
        I sure hope so..."
        """ 
```

### So how does the QuestionDetector work?  
Simply use the .detect() method!    
The results are going to be a list of `Question` objects.    
In this specific example `IssueQuestion` objects.    


```python
results = detector.detect(text)
results
```




    [<bot.question.issues.IssueQuestion at 0x2223974d348>,
     <bot.question.issues.IssueQuestion at 0x2223974d448>,
     <bot.question.issues.IssueQuestion at 0x2223974d908>]



And all 3 questions from the sample text above have been identified!


```python
[(question.question) for question in results]
```




    ["What is this 'text', you ask?",
     'Did that answer all your questions?',
     'can it help with something you still ask?']



### What is the difference between `IssueQuestion` vs `EmailQuestion` vs `IssueCommentQuestion`? 

The only difference is their `origin` and how they get their `context` attributes.     

Look at [What is this `context` attribute I'm seeing?](b#What-is-this-context-attribute-I'm-seeing?) for more


```python
results[1].__dict__
```




    {'id': '8621376d766242ab9fd740a3698f0dd2',
     'question': 'Did that answer all your questions?',
     'start': 188,
     'end': 223,
     'origin': 'issue',
     'context': None}



### What is this `context` attribute I'm seeing in the Question objects?

Well, that's what the AnswerDetector uses to try and answer each question!  

~To be more specific~

1) When a new User Question is asked and is very similar or identical to the questions archived by using the .detect() method.   
2) Then the context of these archived questions is used as context for the new User Question.   
3) Donkeybot's AnswerDetector tries to find suitable answers!  

For `IssueQuestions` the context are any comments that are part of the same GitHub issue.  
For `IssueCommentQuestion` the context are comments after this specific one where the Question was detected.  
For `EmailQuestions` the context are the bodies of the reply emails to the email where the Question was detected.

Each different Question object has it's own unique `find_context_from_table()` 
method that sets the attribute by following the logic explained above.   

Basically go into the table in our Data Storage and SELECT the context we want.

### Can I use the QuestionDetector for my projects that aren't issue/email/comment related?

Yes!     

But, if you aren't following the issue, email, comment logic Donkeybot follows at the point of writing this.
(end of GSoC '20').    

Then, Donkeybot needs to be expanded to have a `Question` superclass and a `set_contexT()` method fo you to simple set the context without going into some dependand Data Storage.    

If you want to see this in Donkeybot [open an issue](https://github.com/rucio/donkeybot/issues) and suggest it.
I'll see that you've been reading the documentation and that this functionality is needed :D 


## How can I use the Fetchers?

The scripts `fetch_issues.py`, `fetch_rucio_docs.py` do everything explained here. 
See [scripts](https://github.com/rucio/donkeybot/tree/master/scripts) for source code and run the scripts with the '-h' option for info on the arguments they take.  
eg.  

`(virt)$ python scripts/fetch_rucio_docs.py -h`


### How can I create a `Fetcher` ?

Simple, use the `FetcherFactory` and just pick the fetcher type 
- Issue for a GitHub `IssueFetcher`
- Rucio Documentation for a `RucioDocsFetcher`   

What about the `EmailFetcher` ?
- Currently as explained in [How It Works](https://github.com/rucio/donkeybot/blob/master/docs/how_it_works.md) emails are fetched from different scripts run in CERN and not through Donkeybot.


```python
from bot.fetcher.factory import FetcherFactory
```

Let's create a GitHub `IssueFetcher`.


```python
issues_fetcher = FetcherFactory.get_fetcher("Issue")
issues_fetcher
```




    <bot.fetcher.issues.IssueFetcher at 0x1b75c30b6c8>




### How can I fetch GitHub issues?

You need 4 things.
- The **repository** whose issues we are fetching
- A **GitHub API token**. To generate a GitHub token visit [Personal Access Tokens](https://github.com/settings/tokens) and follow [Creating a Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).
- The **maximum number of pages** the fetcher will look through to fetch issues. (default is 201)
- A couple pandas **DataFrames**, one which will hold the issues data and one for the issue comments data.


```python
import pandas as pd
```


```python
repository = 'rucio/rucio' # but you can use any in the format user/repo
token = "<YOUR_TOKEN>"
max_pages = 3
```


```python
(issues_df, comments_df) = issues_fetcher.fetch(repo=repository, api_token=token, max_pages=max_pages)
```

The resulting DataFrames will look like this:


```python
issues_df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 26 entries, 0 to 25
    Data columns (total 7 columns):
     #   Column      Non-Null Count  Dtype 
    ---  ------      --------------  ----- 
     0   issue_id    26 non-null     object
     1   title       26 non-null     object
     2   state       26 non-null     object
     3   creator     26 non-null     object
     4   created_at  26 non-null     object
     5   comments    26 non-null     object
     6   body        26 non-null     object
    dtypes: object(7)
    memory usage: 1.5+ KB
    


```python
comments_df.info()
```

    <class 'pandas.core.frame.DataFrame'>
    RangeIndex: 16 entries, 0 to 15
    Data columns (total 5 columns):
     #   Column      Non-Null Count  Dtype 
    ---  ------      --------------  ----- 
     0   issue_id    16 non-null     object
     1   comment_id  16 non-null     object
     2   creator     16 non-null     object
     3   created_at  16 non-null     object
     4   body        16 non-null     object
    dtypes: object(5)
    memory usage: 768.0+ bytes
    


### How does Donkeybot Fetch Rucio Documentation? 

It's the same process we followed with the `IssueFetcher` only now the factory will create a `RucioDocsFetcher`


```python
from bot.fetcher.factory import FetcherFactory
```


```python
docs_fetcher = FetcherFactory.get_fetcher("Rucio Documentation")
docs_fetcher
```




    <bot.fetcher.docs.RucioDocsFetcher at 0x1b75c43bf48>




```python
token = "<YOUR_TOKEN>"
```


```python
docs_df = docs_fetcher.fetch(api_token=token)
```


### How does Donkeybot save the fetched data?

For this we need to  
**Step 1.** open a connection to our Data Storage  


```python
from bot.database.sqlite import Databae

# open the connection
db_name = 'data_storage'
data_storage = Database(f"{db_name}.db")
```

**Step 2.** Save the fetched issues and comments data.


```python
# save the fetched data
issues_fetcher.save(
    db=data_storage,
    issues_table_name='issues',
    comments_table_name='issue_comments',
)
```

**Step 2.1.** Alternativerly save the documentation data.


```python
# save the fetched data
docs_fetcher.save(db=data_storage, docs_table_name='docs')
```

**Step 3.** Finally close the connection


```python
# close the connection
data_storage.close_connection()
```

**Alternative :** If you don't want to use Donkeybot's Data Storage you can use the `save_with_pickle()` and `load_with_pickle()` methods to achieve the same results.

## What about the workings of the Search Engines?

You can use the script `query.py` to query the search engines and  `create_se_indexes.py` is what creates the Search Engine
indexes for Donkeybot. 
See [scripts](https://github.com/rucio/donkeybot/tree/master/scripts) for source code and run the scripts with the '-h' option for info on the arguments they take.  
eg.  

`(virt)$ python scripts/query.py -h`

### How can I create a Search Engine?

There are 3 types of Search Engines in Donkeybot at the moment:  
- `SearchEngine` which is used to query general documenation ( in our case Rucio Documentation )  
- `QuestionSearchEngine` which is used to query Question objects saved in Data Storage  
- `FAQSearchEngine` which is used to query FAQs saved in Data Storage  

Let's create a `QuestionSearchEngine`


```python
from bot.searcher.question import QuestionSearchEngine
```


```python
qse = QuestionSearchEngine()
qse
```




    <bot.searcher.question.QuestionSearchEngine at 0x2a2cf58a348>



**The QuestionSearchEngine is not yet usable!**    

We need 3 things:   

**Step 1.** Have a pandas **DataFrame** with the column **question** that holds the information we will index. The document id for th QuestionSearchEngine will be a column named **question_id** under corpus.   

*sidenote*: A nice addition to Donkeybot will be the ability to change the name of these columns and have something more general.  
But, this is only needed for the sqlite implementation. If in the future we move to Elasticsearch there is no need.

**Step 2.** Have an open connection to the Data Storage

**Step 3.** `create_index()` or `load_index()` which is the document term matrix of the questions.


```python
# Step 1
import pandas as pd
# example DataFrame
corpus_df = pd.DataFrame({"question_id": [0,1,2,3],
                          "question":["What happened in GSoC 2020 ?",
                                      "How can I create an index ?",
                                      "How can I load an index ?", 
                                      "Why are there so many questions in this example?"], 
                          "answer":["Donkeybot was created!", 
                                    "With the .create_index() method!",
                                    "With the .load_index() method!",
                                    "Because BM25 need enough data to create good tf-df vectors :D"]})
corpus_df
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>question_id</th>
      <th>question</th>
      <th>answer</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>What happened in GSoC 2020 ?</td>
      <td>Donkeybot was created!</td>
    </tr>
    <tr>
      <th>1</th>
      <td>1</td>
      <td>How can I create an index ?</td>
      <td>With the .create_index() method!</td>
    </tr>
    <tr>
      <th>2</th>
      <td>2</td>
      <td>How can I load an index ?</td>
      <td>With the .load_index() method!</td>
    </tr>
    <tr>
      <th>3</th>
      <td>3</td>
      <td>Why are there so many questions in this example?</td>
      <td>Because BM25 need enough data to create good t...</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Step 2
from bot.database.sqlite import Database
data_storage = Database('your_data_storage.db')
```


```python
# Step 3 create the index!
qse.create_index(
        corpus=corpus_df, db=data_storage, table_name="corpus_doc_term_matrix"
    )
qse.index
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>terms</th>
    </tr>
    <tr>
      <th>question_id</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>gsoc, happen</td>
    </tr>
    <tr>
      <th>1</th>
      <td>creat, index</td>
    </tr>
    <tr>
      <th>2</th>
      <td>load, index</td>
    </tr>
    <tr>
      <th>3</th>
      <td>exampl, mani, question</td>
    </tr>
  </tbody>
</table>
</div>




```python
data_storage.close_connection()
```

Now the QuestionSearchEngine is ready!

### How can I query the Search Engine?

Let's try and query the `QuestionSearchEngine` we just created above


```python
query = "Anything cool that happened in this year's GSoC?" # whatever you want to ask
top_n = 1 # number of retrieved documents 
```

And just run the `.search()` method.


```python
qse.search(query, top_n)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>question_id</th>
      <th>question</th>
      <th>answer</th>
      <th>bm25_score</th>
      <th>query</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>0</td>
      <td>What happened in GSoC 2020 ?</td>
      <td>Donkeybot was created!</td>
      <td>1.783785</td>
      <td>Anything cool that happened in this year's GSoC?</td>
    </tr>
  </tbody>
</table>
</div>






[Move back to documentation homepage](https://github.com/rucio/donkeybot/tree/master/docs)