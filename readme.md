[![Build Status](https://travis-ci.com/pennsignals/microservice.svg?branch=master)](https://travis-ci.com/pennsignals/microservice)
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

# Unit Test

    $ docker-compose -f docker-compose.unit.test.cfg build && docker-compose -f docker-compose.unit.test.cfg  run --rm unit_test

# Workflow

## Import python modules:

The project (where setup.py and the default location for notebooks exist) is not the same as the python module (the nested directory named `microservice`). To import python modules from the microservice, run this snippet in you jupyter notebook:

```python
import sys
sys.path.append('./microservice')
```

... and then import python modules like this:

```python
from microservice import (
	Input,
	Output,
	Microservice
)
```
