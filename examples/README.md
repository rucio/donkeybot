# Running the notebooks

If you want to run the notebooks yourself you need to have a 'developer mode' installation of Donkeybot on your machine.

Inside a Jupyter notebook cell:   
**Step 1.** Check the directory you are in with `os.getcwd()` .    

**Step 2.** If you're inside `\examples` run `os.chdir('..')`  
Which moves us back to the top level directory.   

**Step 3.** Run `pip install -e .`   
That will look for setup.py in the current directory and install Donkeybot in developer mode :)   

See the [official docs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more info on the the pip install -e option.
