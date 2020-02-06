ARG BASE_IMAGE=605735537041.dkr.ecr.us-east-1.amazonaws.com/python
ARG BASE_IMAGE_VERSION=v3.6

#Use the base image for python pushed to ecr
FROM ${BASE_IMAGE}:${BASE_IMAGE_VERSION}

RUN apk add --no-cache --virtual .build-deps gcc musl-dev zlib libjpeg-turbo-dev libpng-dev freetype-dev git lcms2-dev libwebp-dev harfbuzz-dev fribidi-dev tcl-dev tk-dev
RUN mkdir knowledge_repo_server \
    && cd ./knowledge_repo_server \
    && mkdir analytics repo
COPY . ./knowledge_repo_server
RUN pip3 install -U pip \
    && pip3 install knowledge-repo \
    && knowledge_repo --repo repo init

ENTRYPOINT knowledge_repo --repo ./repo runserver
