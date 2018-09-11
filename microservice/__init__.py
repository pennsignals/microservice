"""Microservice."""

from .core import Microservice as BaseMicroservice


class Microservice(BaseMicroservice):

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
        raise NotImplementedError()

    @classmethod
    def job(cls):
        raise NotImplementedError()

