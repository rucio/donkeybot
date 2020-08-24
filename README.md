# Donkeybot: Rucio Support Bot with NLP (GSoC Project)

![license](https://img.shields.io/badge/License-Apache%202-blue.svg)
![language](https://img.shields.io/badge/python-3.x-green.svg)

Donkeybot is an end-to-end Question Answering system that utilizes multiple data sources, an FAQ table and transfer-learning language models like BERT to answer Rucio support questions.

Currently only a prototype and not ready for production.

## Introduction

The aim of the project under GSoC 2020 is to use Native Language Processing (NLP) to develop an intelligent bot prototype able to provide satisfying answers to Rucio users and handle support requests up to a certain level of complexity, forwarding only the remaining ones to the experts.

Donkeybot can be expanded and applied as a Question-Answering system for your needs. Changes in the code are required to use Donkeybot for your specific use case and data. Current implementation applies to Rucio specific data sources.

## Full Documentation

See the full [documentation](./docs/README.md) for examples, operational details and other information.

## Google Summer of Code

See [FAQ: GSoC](./docs/faq_gsoc.md) for a detailed timeline, problems faced, future improvements and other information.

## Demo 

You can try asking Donkeybot yourself! 
``` bash
$  python .\scripts\ask_donkeybot.py
```

You will see output similar to the following example:  
- Question : "How are Rucio Users authenticated?"   
- BERT model : [distilbert-base-cased-distilled-squad](https://huggingface.co/distilbert-base-cased-distilled-squad)  
- top_k : 1
- Answers : 
  - 1 answer from 2x Rucio Documentation + 2x Past Questions retrieved docs 
  - 1 answer from [FAQ](./data/faq.json)

![demo](./docs/img/demo.gif)

More examples and information can be found in the [How To Use](./docs/how_to_use.md) section.

Example source code can be found in the [donkeybot-examples](https://github.com/rucio/donkeybot/tree/master/donkeybot-examples) module.


## What does it do?
See [How it Works](./docs/how_it_works.md) for more detailed information.

1) **Data storage** : Creates a Question-Answering (QA) Rucio specific data storage for our domain data. Current implementation is in SQLite for fast prototyping. Data sources include secure and anonymous [support emails](https://rucio.cern.ch/contact.html) from Rucio users, [Rucio GitHub issues](https://github.com/rucio/rucio/issues) and [Rucio documentation](https://rucio.readthedocs.io/en/latest/).
   
2) **Question detection** : Provides module for question detection from within a given text. Currently used to extract past user questions from email and GitHub issues by using regex patterns.
   
3) **Document Retrieval** : Utilizes [Okapi BM25](https://en.wikipedia.org/wiki/Okapi_BM25) algorithm from [rank-bm25](https://pypi.org/project/rank-bm25/) for the retrieval of most similar documents - be it previously asked questions or documentation - to be used as context by the answer detection module.
   
4) **Answer Detection** : Follows a transfer-learning approach, using pre-trained transformer models such as BERT from [Hugginface transformers](https://github.com/huggingface/transformers) to provide the user with top-k number of answers based on the retrieved documents. Additionally, an FAQ-based supervised approach is provided to tackle more specific and common questions that the user might ask.

5) **FAQ creation** : User can use a very simple GUI as an interface to insert FAQ questions, re-index the search engine and expand Donkeybot's data storage.

## Build

**Step 1:** Clone the repository to your development machine and configure it:
``` bash
$ git clone https://github.com/rucio/donkeybot.git
$ cd donkeybot
```
**Step 2:** Download the requirements 
``` bash
$ pip install -r requirements.txt
```
You also need to have [PyTorch]( https://pytorch.org/ ) installed.

**Step 3:** Build and populate Donkeybot's data storage. 
``` bash
$ python scripts/build_donkeybot -t <GITHUB_API_TOKEN>
```
- To generate a GitHub token visit [Personal Access Tokens](https://github.com/settings/tokens) and follow [Creating a Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).


See the [Getting Started](./docs/getting_started.md) page for more details on building Donkeybot, troubleshooting, installing PyTorch and initiating the developer mode.

## Bugs and Feedback

For bugs, questions and discussions please use the [GitHub Issues](https://github.com/rucio/donkeybot/issues).

 
## LICENSE

Licensed under the Apache License, Version 2.0;

<http://www.apache.org/licenses/LICENSE-2.0>
