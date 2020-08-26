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

[Move back to documentation homepage](https://github.com/rucio/donkeybot/tree/master/docs)