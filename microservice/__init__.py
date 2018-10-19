"""Microservice."""

from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from os import stdout

from .core import (
    garbage_collection,
    Microservice as BaseMicroservice,
    Model as ModelBase,
)

from pkg_resources import (
    DistributionNotFound,
    get_distribution,
)

basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


class Model:

    def __init__(self):
        """Initialize model."""
        raise NotImplementedError()

    @garbage_collection
    def __call__(self):
        """Run model."""
        raise NotImplementedError()


class Microservice(BaseMicroservice):
    """Microservice."""

    CONFIGURATION = {
        ('MICROSERVICE_CONFIGURATION', '--cfg'): {
            'default': './local/microservice.cfg',
            'dest': 'configuration',
            'help': 'Yaml file for configuration.',
            'type': str,
        },
    }

    DESCRIPTION = 'Describe your microservice here.'

    ARGS = {
        **CONFIGURATION,
        # **More.ARGS,
        # **EventMore.ARGS,
    }
