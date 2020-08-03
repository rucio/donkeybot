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

# Requirements
* [Python 3 ](https://www.python.org/downloads/windows/), 64bit required for correct installation of PyTorch on Windows.
* To install PyTorch head over to https://pytorch.org/ and follow the quick start guide for your operating system.
* Run the following command on the terminal:
    ``` bash
    $ pip install -r requirements.txt
    ``` 
# Bot in developer mode

**Step 1:** Creating a virtual enviroment.
``` bash 
# virt is an example name of the virtual enviroment
# command might be 'py' or 'python3' on your machine
$ python -m venv virt 
```

**Step 2:** Activate the enviroment
``` bash
$ source virt/bin/activate
# or on Windows
$ virt/Scripts/activate
```

**Step 3:** Run `setup.py`
``` bash
# make sure setuptools exists inside this venv
$(virt) python -c 'import setuptools'
# create distribution package
$(virt) python setup.py sdist 
# Optional, check whats inside 
$(virt) tar --list -f .\dist\bot-<BOT_VERSION_HERE>.tar.gz
```

**Step 4:** Developer mode 
``` bash
$(virt) python setup.py develop
```
You're now able to run any scripts and imports work correctly