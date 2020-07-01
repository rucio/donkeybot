# Approach

To reach our milestones and successfully create the support bot we need to split the work into two distinct phases. This approach can be generalized and applied to your custom email dataset. Of course this bot is optimized to work with Rucio's support email data and to expand upon it requires important changes in the codebase.

**Phase 1:**  
**The scripts that we use to do Step 1 are under `/scripts/input` and the script for Steps 2-6 in phase 1 is `dataset_creation.py`**

First we need to utilize past email data and setup the infrastructure needed to parse an email, detect questions in it and find suitable answers. Thus, optimizing the bot's performance on our specific use-case. The step by step approach we follow is:  
  
1) Previous support emails are run through a [Name Tagger](name_tagger.md) that hashes user information and keeps user data private. This is done with the help of [Stanford's CoreNLP NER tagger](https://stanfordnlp.github.io/CoreNLP/cmdline.html) to identify user's names and then hash them with md5 through hashlib.
2) These raw anonymized emails are saved into a .db file that hold's email information `( sender, receiver(s), subject, date, body )` and is treated as input to the next step.
3) We then read the raw emails from the .db file and parse them one by one through the `EmailParser` from `eparser.py` module. The parser now does the required processing on the raw email data and creates Email objects that hold the following information:
    | Column            | Description                                                               |   
    | :----             | :-----------                                                              |
    | email_id          | unique id for the email                                                   |
    | sender            | email's sender                                                            |
    | receiver          | email's receiver(s)                                                       |
    | subject           | email's subject                                                           |
    | body              | email's body                                                              |
    | email_date        | email's date                                                              |
    | first_email       | 0/1 if it's the first email sent                                          |
    | reply_email       | 0/1 if it's a reply email                                                 |
    | fwd_email         | 0/1 if it's a forwarded email                                             |
    | clean_body        | processed body of the email that doesn't hold quoted bodies of past emails|
    | conversation_id   | the id of the conversation the email is a part of                         | 
    
    For more information on email parsing and `eparser.py` look at the [Email Parser](email_parser.md) documentation.
4) These are now saved in our current implementation on the 'emails' table under 'dataset.db' by using sqlite.      
More information on how we save/load data with `database.py` can be found in the [Sqlite Wrapper](sqlite_wrapper.md) documentation.  .

5) The next step is to try and find any questions that exists in the clean_body of the parsed Email objects. `QuestionDetector` from `analyzer.py` is the class used to detect and create Question objects that hold the following information:
    | Column        | Description                                                               |   
    | :----         | :-----------                                                              |
    | question_id   | unique id for the question                                                |
    | email_id      | question's email                                                          |
    | clean_body    | clean body where the question resides                                     |
    | question      | text of the question                                                      |
    | start         | start index of the question (in clean_body)                               |
    | end           | end index of the question (in clean_body)                                 |
    | context       | text where answer of a given of the question probably exists.             |
    
    For more information on question detection and `analyzer.py` look at the [Question Detection](question_detector.md) documentation.
6) These Questions are then also saved on the `dataset.db` under the 'questions' table. 

**This is where my code up until the end of June stops and documentation below is what we are probably going to do. Take everything below with a grain of salt and not as representative to the final product** 

7) The next step is to identify the Answers that correspond to the Question objects which is done with the help of a couple of different methods.
    * Unsupervised approach : BERT fine tuned on SQuaD is run on our questions and context pairs to try and automatically detect an answer for each given question. This is probably done after some additional processing on the context and the question. The goal is to try and match question answer pairs on nicely formulated questions/answers without any supervision
    * Supervised approach	: Since the questions asked and the subfield they are asked on is quite special we'll most probably need to manually label answers to frequent questions. To find frequent questions we of course need to use similarity metrics and analyze our current data and then manually add answers to create the table. Ideally the unsupervised approach to answer generation will be helpful here by providing us we probable answers.  

Since the goal is to provide the users with correct information the FAQ and supervised approach is going to be our main goal and the first way that an answer is paired with a question. 
Let's move on to phase 2 which discusses how everything above and more importantly how BERT and the FAQ table are used in the pipeline for the Answer generation.

**Phase 2:**  
This phase is basically the deployment phase of the bot, where it is fully functional and able to run in real-time to supply suitable answers to user support emails and requests. Each step is run in succession to the one before and a priority queue is followed for each request that comes in.

1) When a support email is received it goes through the `EmailParser` and is then saved on 'emails' table under 'dataset.db'
2) Then `QuestionDetector` is run on the clean_body of the email and if a question is found we move on to the matching
3) The matching of questions and answers is done by the `Answer Factory` which
   1) Tries to match it to existing question in FAQ
   2) Tries to find answer through context of similar conversations  
   3) Tries to find answer through context in Rucio's docs/issues under 
4) If a Named Entity Recognition  algorithm has been created for DID's, RSE's and file operation detection by the end of the project we can try and supply different type of  answers that are specific to each use case. Through either with a more generic approach or integration with Rucio's monitoring system to check status and metadata of the requested information and supply it to the user.
5) The Answer is sent to the user in the form of an Email or if no answer is provided by the bot the actual request is forwarded to the experts.