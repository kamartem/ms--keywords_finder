ARG PYTHON_VERSION=3.8.5-buster

FROM python:${PYTHON_VERSION}

COPY ./src/requirements.txt /requirements.txt

RUN pip install -U pip && pip install -r /requirements.txt

COPY /src "/opt/app"

WORKDIR "/opt/app"

EXPOSE 8000
