FROM python:3.7.11-alpine
MAINTAINER Andrew Fitzpatrick

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt

# permanent dependencies
RUN apk add --update --no-cache postgresql-client

# dependencies used just for installing build dependencies
RUN apk add --update --no-cache --virtual .tmp-build-deps \
        gcc libc-dev linux-headers postgresql-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /app
WORKDIR /app
COPY ./app /app

RUN adduser -D user
USER user
