## Contents
- [Contents](#contents)
- [How can I use the QAInterface / AnswerDetector?](#how-can-i-use-the-qainterface--answerdetector)
- [How do the Search Engines work?](#how-do-the-search-engines-work)
- [Can I just query the QuestionDetector?](#can-i-just-query-the-questiondetector)
- [Is there a way to add more FAQs?](#is-there-a-way-to-add-more-faqs)
- [How are the support Emails fetched?](#how-are-the-support-emails-fetched)
- [Do you hash private user information?](#do-you-hash-private-user-information)
- [What do you mean by 'parsing support Emails'?](#what-do-you-mean-by-parsing-support-emails)
- [Can I fetch GitHub issues from any repo?](#can-i-fetch-github-issues-from-any-repo)
- [And can I parse GitHub Issues?](#and-can-i-parse-github-issues)
- [How can I fetch Rucio Documentation?](#how-can-i-fetch-rucio-documentation)
- [What parsing is done to the Rucio Documentation?](#what-parsing-is-done-to-the-rucio-documentation)
- [Can I use Donkeybot for some text processing?](#can-i-use-donkeybot-for-some-text-processing)

## How can I use the QAInterface / AnswerDetector?
Explain ask_donkeybot.py and how to use the QAInterface for more detailed fine tuning
and chaining the parameters of how many documents are retrieved etc.

Downloading and utilizing other models?
Expand code to do this automatically?

Give AnswerDetector examples

## How do the Search Engines work?
How to create/load indexes and how to query the search engines

## Can I just query the QuestionDetector?
How to detect question in any text
How we detect in GitHub issues and pas Rucio support emails
Give examples obviusly for everything in this page

## Is there a way to add more FAQs?
Example gui ( create script that runs -> /faq/gui )

## How are the support Emails fetched?
Explain that code under scripts/input is used from CERN's side

## Do you hash private user information?
- OFC explain
Stanford's NER tagger and how to use/deploy etc.

## What do you mean by 'parsing support Emails'?
- Explain that the raw emails need to change and how/what we do
- email chain creation/conversation creation reply cleaning
Explain what is added
Email object class diagram?

## Can I fetch GitHub issues from any repo? 
- Yes explain
simple command explanation say that it applies for any github project

## And can I parse GitHub Issues?
- yes but parsing is only for preparing the data for Donkeybot
- If you just want the raw data use the fetch script
Explain new
Issue object class diagram?
IssueComment object class diagram?

## How can I fetch Rucio Documentation?
Explain that it currently works only for rucio
and that it doesn work for apis
Command that does this

## What parsing is done to the Rucio Documentation?
RucioDoc object class diagram?

## Can I use Donkeybot for some text processing?
Explain that this, under utils is used in our parsers