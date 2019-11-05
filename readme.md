[![Build Status](https://travis-ci.com/pennsignals/microservice.svg?branch=master)](https://travis-ci.com/pennsignals/microservice)
[![Container Status](https://quay.io/repository/pennsignals/microservice/status)](https://quay.io/repository/pennsignals/microservice)

# Customize

Create an private empty git repo for your project on github:
- `git clone git@github.com:pennsignals/microservice.git <project>`
- Update `.git/config` line `url = git@github.com:pennsignals/microservice.git` to `git@github.com:pennsignals/<project>.git`
- `git mv src/project src/<project>`
- Update `setup.cfg` line `--cov project` to `--cov <project>`
- Update `setup.py` line `url=https://github.com/pennsignals/microservice` to `https://github.com/pennsignals/<project>`
- Update `setup.py` console scripts for project:
```
        'console_scripts': (
            (
                '<project> = '
                '<project>:Micro.run_on_schedule'),
            (
                '<project>.run_once_now = '
                '<project>:Micro.run_once_now'),
        ),

```
- Update `production.nomad` replacing `project` with `<project>`
- Inspect `production.nomad` secrets and update `predict` or `clarity` with appropriate names for you project
- Update the Build Status badge at the top of this file: `https://travis-ci.com/pennsignals/microservice.svg?branch=master` to `https://travis-ci.com/pennsignals/<project>.svg?branch=master`
- Update the Container Status badge at the top of this file: `https://quay.io/repository/pennsignals/microservice/status)` to `https://quay.io/repository/pennsignals/<project>/status)`
- Update the Container Status badge again once you get the markdown at the bottom of the page from quay at https://quay.io/repository/pennsignals/<project>?tab=settings private repositories need a token in the status link that the microservice template does not need.
- `git push -u origin master`


# Startup

## Jupyter with Mongo:

    $ docker-compose run --rm --service-ports jupyter

## Microservice with Mongo:

    $ docker-compose run --rm --service-ports <project>

## Both with Mongo:

    $ docker-compose up

# Shutdown

    $ docker-compose down

# Unit Test

    $ docker-compose -f docker-compose.unit.test.cfg build && docker-compose -f docker-compose.unit.test.cfg  run --rm unit_test

## Import python modules in jupyter:

The project (where setup.py and the default location for notebooks exist) is not the same as the python module (the nested directory named `microservice`). To import python modules from the microservice, run this snippet in you jupyter notebook:

```python
import sys
sys.path.append('./src/<project>')
```

... and then import python modules like this:

```python
from <project> import (
	Input,
	Output,
	Microservice
)
```
