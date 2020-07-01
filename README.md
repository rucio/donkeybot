# DonkeyBot
**Rucio Support Bot with NLP (GSOC Project)**

Different levels of expert support are available for users in case of problems. When satisfying answers are not found at lower support levels, a request from a user or a group of users can be escalated to the Rucio support. Due to the vast amount of support requests, methods to assist the support team in answering these requests are needed.  

The aim of the project under GSoC 2020 is to use Native Language Processing (NLP) to develop an intelligent bot prototype able to provide satisfying answers to Rucio users and handle support requests up to a certain level of complexity, forwarding only the remaining ones to the experts. 

Additional information on the project's description and initial milestones for the student are provided on [Rucio Support Bot proposal.](https://github.com/TomasJavurek/hsf.github.io/blob/master/_gsocproposals/2020/proposal_RucioSupportBot.md)

You can find everything related to the bot under our [documentation](/docs/home.md) and our wiki.

# Setting up the repository

**Step 1:**  Fork the [repository](https://github.com/rucio/bot-nlp) on Github.

**Step 2:** Clone the repository to your development machine and configure it:
``` bash
$ git clone https://github.com/<YOUR_USER>/bot-nlp/
$ cd bot-nlp
$ git remote add upstream https://github.com/rucio/bot-nlp.git
```