# DonkeyBot

The aim of the project under GSoC 2020 is to use Native Language Processing (NLP) to develop an intelligent bot prototype able to provide satisfying answers to Rucio users and handle support requests up to a certain level of complexity, forwarding only the remaining ones to the experts. This project's approach to end-to-end question detection and answer generation can be generalized to a number of use cases and scenarios with of course changes to the code that is tailor to Rucio's use case.

[Rucio](https://rucio.github.io/) is an open source software framework that provides scientific collaborations with the functionality to organize, manage, and access their volumes of data. Data in Rucio is organized using Data Identifiers (DIDs) which have three levels of granularity viz.: files, datasets and containers, respectively. Datasets are used to organise sets of files in groups and to facilitate bulk operations such as transfers or deletions. Users are permitted to perform certain actions on the DIDs such as downloads, uploads or transfers. Different levels of expert support are available for users in case of problems. When satisfying answers are not found at lower support levels, a request from a user or a group of users can be escalated to the Rucio support. Due to the vast amount of support requests, we are looking into methods to assist the support team in answering these requests. 

Additional information on the project's description and initial milestones for the student are provided on [Rucio Support Bot proposal.](https://github.com/TomasJavurek/hsf.github.io/blob/master/_gsocproposals/2020/proposal_RucioSupportBot.md)
Also, more information about Rucio and how to contribute can be found in the corresponsing [documentation](https://rucio.readthedocs.io/en/latest/).


# Table of Contents
* Getting started
  * Folder Structure
  * Installation
  * Operation
  * [Architecture](architecture.md)
  * Progress Report
  * Reading List
* Algorithms
  * [Name Hashing](name_tagger.md)
  * [Email Parser](email_parser.md)
  * [Question Detection](question_detector.md)
  * [Answer Detection](answer_detection.md)
  * Topic Modeling (LDA)
* General
  * [Approach](approach.md)
  * [Sqlite Wrapper](sqlite_wrapper.md)
  * Testing
  * Future Work



