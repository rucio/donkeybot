from setuptools import setup, find_packages
import os


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="donkeybot",
    version="0.1.0",
    description="Rucio Support Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(where="lib"),
    package_dir={"": "lib"},
    install_requires=[
        "pandas",
        "numpy",
        "nltk",
        "rank_bm25",
        "requests",
        "transformers",
        "uuid"
        # for torch you need to download based on https://pytorch.org/ quickstart guide
    ], 
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
