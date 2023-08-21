FROM python:3.8.5

WORKDIR /code
COPY . /code
RUN python3 -m pip install -r /code/requirements.txt