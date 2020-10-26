FROM python:3.8.5
RUN pip --no-cache-dir install --upgrade pip && \
    pip --no-cache-dir install --upgrade setuptools wheel
WORKDIR /docker
COPY . /docker
RUN python setup.py sdist && \
    python setup.py develop && \  
    pip install -r requirements.txt && \
    python scripts/build_donkeybot.py -t <YOUR_GITHUB_API_TOKEN>