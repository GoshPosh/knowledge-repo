ARG BASE_IMAGE=605735537041.dkr.ecr.us-east-1.amazonaws.com/python
ARG BASE_IMAGE_VERSION=v3.6

#Use the base image for python pushed to ecr
FROM ${BASE_IMAGE}:${BASE_IMAGE_VERSION}

ARG BASE_DIR=/goshposh
ARG ENV_ARG
ARG PORT_ARG=7000

COPY ./ ${BASE_DIR}/knowledge-repo

# RUN apk add --no-cache --virtual .build-deps gcc \
#     py-mysqldb musl-dev zlib libjpeg-turbo-dev libpng-dev \
#     freetype-dev git lcms2-dev libwebp-dev harfbuzz-dev \
#     fribidi-dev tcl-dev tk-dev  mariadb-dev build-base

RUN apk add --virtual .build-deps gcc py-mysqldb musl-dev zlib libjpeg-turbo-dev libpng-dev \
    freetype-dev git lcms2-dev libwebp-dev harfbuzz-dev \
    fribidi-dev tcl-dev tk-dev  mariadb-dev build-base

RUN mkdir -p ${BASE_DIR}/knowledge_repo_server \
    && cd ${BASE_DIR}/knowledge_repo_server \
    && mkdir analytics repo log

RUN pip3 install -U pip \
    && pip3 install werkzeug==0.16.0 \
    && pip3 install PyMySQL \
    && pip3 install mysqlclient \
    && pip3 install knowledge-repo \
    && pip3 install requests_oauthlib \
    && knowledge_repo --repo repo init

ENV ENV=$ENV_ARG
ENV PORT=$PORT_ARG

EXPOSE ${PORT}

ENV SERVER_NAME=ae8e8536c4e5611ea8d9212bb7211a17-1956233292.us-east-1.elb.amazonaws.com:7000
ENV SQLALCHEMY_DATABASE_URI=mysql+pymysql://admin:goshposh@qa-knowledge.cfixyr8sjfcf.us-east-1.rds.amazonaws.com/knowledge
COPY docker/pm_scripts/config.py config.py
COPY knowledge_repo knowledge_repo
ENTRYPOINT knowledge_repo --repo ./repo deploy --config config.py --engine flask


