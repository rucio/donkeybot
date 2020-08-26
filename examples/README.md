# Running the notebooks

If you want to run the notebooks yourself you need to have a 'developer mode' installation of Donkeybot on your machine.

**Step 1.** Check the dir you are in `os.getcwd()`.    
**Step 1.** If you're inside `\examples` simply `os.chdir('..')` more back to the top level directory   
**Step 3.** In a jupyter notebook run 
`pip install -e .` that will look for setup.py in the current directory and install Donkeybot in developer mode :)   

See the [official docs](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more info on the the pip install -e option.
