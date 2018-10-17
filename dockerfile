FROM quay.io/pennsignals/alpine-3.8-python-3.7-datascience-mssql:v2.0
WORKDIR /tmp
COPY .git .
COPY readme.md .
COPY requirements.txt .
COPY setup.py .
COPY setup.cfg .
COPY local ./local
COPY microservice ./microservice
COPY tests ./tests
RUN pip install --no-cache-dir --requirement requirements.txt
