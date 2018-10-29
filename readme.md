[![Build Status](https://travis-ci.com/pennsignals/microservice.svg?token=FIXME&branch=master)](https://travis-ci.com/pennsignals/microservice)
[![Container Status](https://quay.io/repository/pennsignals/microservice/status?token=FIXME "Docker Repository on Quay")](https://quay.io/repository/pennsignals/microservice)


# Startup

## Jupyter with Mongo:

    $ docker-compose run --rm --service-ports jupyter

## Microservice with Mongo:

    $ docker-compose run --rm --service-ports microservice

## Both with Mongo:

    $ docker-compose up

# Shutdown

    $ docker-compose down
