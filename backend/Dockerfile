ARG PYTHON_VERSION=3.10-bullseye

FROM python:${PYTHON_VERSION}

COPY ./requirements.txt /requirements.txt

RUN pip install -U pip && pip install -r /requirements.txt

COPY .. "/opt/"

WORKDIR "/opt"

EXPOSE 8000
