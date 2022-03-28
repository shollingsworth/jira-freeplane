FROM python:3.9.11

COPY . /app
WORKDIR /app
RUN pip3 install --upgrade pip
RUN pip install -U setuptools setuptools_scm wheel
RUN pip3 install .
