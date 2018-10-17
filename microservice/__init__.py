"""Microservice."""

from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from os import stdout

from .core import Microservice as BaseMicroservice

from pkg_resources import (
    DistributionNotFound,
    get_distribution,
)

basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


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

    ARGS = {
        **CONFIGURATION,
        # **More.ARGS,
        # **EventMore.ARGS,
    }

    @classmethod
    def main(cls):
        """Run job inside scheduler from configuration."""
        raise NotImplementedError()

    @classmethod
    def job(cls):
        """Run job from configuration."""
        raise NotImplementedError()
