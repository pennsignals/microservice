FROM quay.io/pennsignals/alpine-3.8-python-3.7-datascience-mssql:7.0
WORKDIR /tmp
COPY .git ./.git
COPY local ./local
COPY src ./src
COPY tests ./tests
COPY readme.md .
COPY setup.cfg .
COPY setup.py .
RUN apk add git && \
    pip install --no-cache-dir "."
