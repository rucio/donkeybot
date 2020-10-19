FROM python:3.8.5
RUN pip --no-cache-dir install --upgrade pip && \
    pip --no-cache-dir install --upgrade setuptools wheel
WORKDIR /src
COPY . /src
RUN python setup.py sdist
RUN python setup.py develop
RUN pip install -r requirements.txt
