# Bot package


## Bot in developer mode

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
$(virt) tar --list -f .\dist\DonkeyBot-<BOT_VERSION_HERE>.tar.gz
```

**Step 4:** Developer mode 
``` bash
$(virt) python setup.py develop
```
You're now able to run any scripts and imports work correctly