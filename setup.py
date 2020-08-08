from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='DonkeyBot',
    version='0.1.0.dev1',
    description="Rucio Support Bot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=[
          'pandas',
          'numpy',
          'nltk',
          'rank_bm25',
          'requests',
          'transformers',
          'uuid'
        # for torch you need to download based on https://pytorch.org/ quickstart guide
      ],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Natural Language :: English',
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)