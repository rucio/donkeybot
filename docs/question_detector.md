# Question Detection

One of the most important steps in automatically answering Rucio users support email questions is to be able to actually detect the questions being asked. To help us achieve this `QuestionDetector` was created and the code resides in `analyzer.py`.
`QuestionDetector` uses regex patterns to try and match user questions. Additional question identification approaches where tested such as using the question identifier based on chapter 6 section 2.2 of the [Natural Language Toolkig Book](http://www.nltk.org/book/ch06.html) but where not as consistent. Since the main goal is to create a prototype which is as correct with its responses as possible we didn't want to add more noise and label text as a question when it is in fact not. Thus, regex patterns based on question marks and W5H (who, what, where..) words is the way to go. 


Two different regex patterns where used and more/less can be appended easily. These both try and identify questions, one without having applied any processing to the text and the second having lowered the text. It is important to note that the [Punkt Sentence Tokenizer](https://www.nltk.org/_modules/nltk/tokenize/punkt.html) from [NLTK](https://www.nltk.org/) was used to split the text into sentences more easily readable by `QuestionDetector`. 

The `pipeline` to question detection is as follows:   
1) `QuestionDetector's` method named `detect(self, text)` is used on the text where a question might reside in. This then applies the regex patterns in a step by step manner.  
   - The first regex pattern `'[A-Z][a-z][^A-Z]*[?]$'` tries to find the substring inside a sentece that starts with some uppercase letter, is followed by lowercase letters, doesn't contain more uppercase letters and then ends with a question mark `?`. This is done because of the abstract nature of many emails that have missing punctuation, many code snippets, urls etc. that troubles the `Punkt Sentence Tokenizer` and results in sentences that are noisy. This regex pattern gives us very good precision on the selected text and performs well on our emails set, which is our goal.
   - The second regex pattern `'(how |wh|can |could |do |does |should |would |may |is |are |have |has |will |am ).*[?]$'` while longer, is quite simple. The idea is to first lower the text and then try and match the substring inside text that starts with  `how, wh, can ...` W5H and other common question words and ends with a question mark `?`.

    Since it is very important to not match the same questions more than once, when a question is identified at any point, the substring of the question inside the text is replaced with spaces `' '`. We basically use padding in the text to keep the same length and ensure correctness of the `Question object's` starting and ending indexes. This successfully 'hides' previously identified questions from regex patterns that have yet to be used. A supervised approach has been followed after question identification to analyze the results of the regex patterns and evaluate them.

2) Once a question has been detected we check to see if it's part of an exception. `EXCEPTIONS_REGEX` is an attribute of the `QuestionDetector` and is a list of regex patterns that should never be regarded as questions. At this point the only regex pattern here is `URL_REGEX`. This basically means that if for some odd reason our question matching regex patterns identify a substring of a url as a question, perhaps if the url has `?` question marks, we apply the check and don't regard said substring as a `Question object`. `EXCEPTIONS_REGEX` can easily be expanded upon and the code already exists to regard any patterns inside this list as exceptions. For example once regex patterns for DIDs, RSEs etc are implemented they can be added here. For more information on what DIDs and RSEs are check [Rucio's documentation](https://rucio.readthedocs.io/en/latest/index.html).

3) If all checks are passed, a `Question object` is created that holds the following information
    | Column        | Description                                                               |   
    | :----         | :-----------                                                              |
    | question_id   | unique id for the question                                                |
    | email_id      | question's email                                                          |
    | clean_body    | clean body where the question resides                                     |
    | question      | text of the question                                                      |
    | start         | start index of the question (in clean_body)                               |
    | end           | end index of the question (in clean_body)                                 |
    | context       | text where answer of a given of the question probably exists.             |

We should note that since the `detect(text)` method of `QuestionDetector` doesn't take an `Email object` as input but rather a simple string, the attributes `(email_id, question_id, clean_body, context)` of a `Question object` are added outside of the `QuestionDetector` and setters from the `Question` class are used. We wanted detect to take a string so that it's more generalized and can be used in a number of cases.

4) Finally, `detect(text)` method returns a list of `Question objects` or empty, for any questions found inside text.

---
##### Additional information about the `context` attribute of an email and the `Question` class.

The `context` of a  `Question object` is basically the text in which the answer to the question most probably resides in. This is used as input to models like [BERT](https://en.wikipedia.org/wiki/BERT_(language_model)), [RoBERTa](https://arxiv.org/abs/1907.11692), [DistilBERT](https://arxiv.org/abs/1910.01108) etc. These are all state of the art models and a very good implementation of them can be found for both [PyTorch](https://pytorch.org/) and [Tensorflow](https://www.tensorflow.org/) is [Huggingface Transformers](https://github.com/huggingface/transformers).  

To get our question's `context` we utilized the `conversation_id` and `email_date` of the email. Basically, the context is the `clean_body` of all the emails that belong to the same conversation and come after the the email where the question has been asked. This is logical since the response to an email with a question, probably by an expert, holds the answer to the question. Additional processing of the context will surely be done, since each model has its own restrictions (for example BERT's default MAX_LENGTH of the context is 512 tokens) and more cleaning is needed to get good results. 

For more information about Answer Generation look at the [documentation](answer_detection.md).





