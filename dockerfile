FROM quay.io/pennsignals/alpine-3.8-python-3.7-datascience-mssql:v1.0
WORKDIR /tmp
COPY readme.md .
COPY requirements.txt .
COPY setup.py .
COPY setup.cfg .
COPY local ./local
COPY project ./project
COPY tests ./tests
RUN pip install --no-cache-dir --requirement requirements.txt
