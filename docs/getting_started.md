# Contents
- [Contents](#contents)
- [Build](#build)
- [Contributing](#contributing)
- [Developer mode](#developer-mode)
- [Testing](#testing)

# Build
**Step 1:**  A 64 bit [Python 3 ](https://www.python.org/downloads/windows/) installation is required by PyTorch.
   
**Step 2:** To install PyTorch head over to https://pytorch.org/ and follow the quick start guide based on your operating system.  
``` python
# versions used in development 
torch==1.6.0  --find-links https://download.pytorch.org/whl/torch_stable.html
torchvision==0.7.0  --find-links https://download.pytorch.org/whl/torch_stable.html
```

**Step 3:** Clone the repository to your development machine.
``` bash
$ git clone https://github.com/rucio/donkeybot.git
$ cd donkeybot
```

**Step 4:** For additional requirements run :
``` bash
$ pip install -r requirements.txt
``` 
    
**Step 5:** Build and populate Donkeybot's data storage :  
``` bash
$ python scripts/build_donkeybot -t <GITHUB_API_TOKEN>
```
To generate a GitHub token visit [Personal Access Tokens](https://github.com/settings/tokens) and follow [Creating a Personal Access Token](https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token).


# Contributing
For aspiring contributors make sure you've forked Donkeybot on your account.

**Step 1:**  Fork the [repository](https://github.com/rucio/donkeybot) on Github.

**Step 2:** Clone the repository to your development machine and configure it :
``` bash
$ git clone https://github.com/<YOUR_USER>/donkeybot/
$ cd donkeybot
$ git remote add upstream https://github.com/rucio/donkeybot.git
```

# Developer mode

For development and testing purposes you need to have the bot installed as a package under a virtual environment (venv).

**Step 1:** Creating a virtual enviroment   
``` bash 
# virt is the name of the virtual environment, you can change it.
$ python -m venv virt 
```

**Step 2:** Activate the enviroment   
``` bash
# on Linux/macOS
$ source virt/bin/activate
# on Windows
$ virt/Scripts/activate
```

**Step 3:** Run setuptools   
``` bash
# make sure setuptools exists inside this venv
$(virt) python -c 'import setuptools'
# create distribution package
$(virt) python setup.py sdist 
# developer mode
$(virt) python setup.py develop
```

**Step 4 (Optional) :**  Check package contents   
``` bash
$(virt) tar --list -f .\dist\donkeybot-0.1.0.tar.gz
```

You're now able to develop and run `donkeybot/scripts` and `donkeybot/tests` correctly.

# Testing
Make sure to run any tests before pushing your code. The testing module used is [pytest](https://docs.pytest.org/en/stable/).  

Run tests :  
``` bash
# Recommended if pytest isn't installed 
$(virt) python setup.py test
```
or 
``` bash
# if not installed
$(virt) pip install pytest 
# then
$(virt) py.test tests
```
and see everything turn green 🟢!
