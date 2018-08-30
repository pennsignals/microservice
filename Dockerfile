FROM quay.io/pennsignals/alpine-3.8-python-3.7-datascience:v2.0
WORKDIR /tmp
COPY ./microservice ./microservice
COPY ./tests ./tests
COPY ./local ./local
COPY ./setup.py ./
COPY ./setup.cfg ./
COPY ./requirements.txt ./
RUN pip install --requirement requirements.txt
