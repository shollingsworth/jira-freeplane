FROM python:3.9.11

RUN pip3 install --upgrade pip
COPY dist/ /dist
RUN pip install $(find /dist -type f -name '*.gz')
