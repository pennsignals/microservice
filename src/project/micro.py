"""Micro."""

from __future__ import annotations
from argparse import (
    ArgumentParser,
    Namespace,
)
from functools import wraps
from pickle import load
from gc import collect
import logging
from os import getenv
from sys import (
    argv as sys_argv,
    stdout,
)

from yaml import safe_load as yaml_loads


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = logging.getLogger(__name__)


def garbage_collection(func):
    """Garbage collection decorator."""
    @wraps(func)
    def _wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        finally:
            collect()
    return _wrapper


def unpickle_from_file(file_name):
    """Return unpickle from file."""
    with open(file_name, 'rb') as fin:
        return load(fin)


class Micro:
    """Micro."""

    CONFIGURATION = {
        ('CONFIGURATION', '--cfg'): {
            'dest': 'configuration',
            'help': 'Yaml file for configuration.',
            'type': str,
        },
    }

    ARGS = {
        **CONFIGURATION,
    }

    DESCRIPTION = 'Micro'

    @classmethod
    def cfg_from_args(cls, args: Namespace) -> dict:
        """Return cfg from args."""
        key = args.configuration
        assert key is not None

        with open(key) as fin:
            cfg = yaml_loads(fin.read())

        cls.patch_args(cfg, args)
        return cfg

    @classmethod
    def from_argv(cls, argv) -> Micro:
        """Return microservice from command line and environment variables."""
        return cls.from_cfg(cls.cfg_from_args(cls.parse_args(argv)))

    @classmethod
    def from_cfg(cls, cfg: dict) -> Micro:
        """Return microservice from cfg."""
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def main(cls) -> None:
        """Main."""
        i = cls.from_argv(sys_argv[1:])
        i()

    @classmethod
    def parse_args(cls, argv: list) -> Namespace:
        """Return parsed args from command line and environment variables."""
        parser = ArgumentParser(description=cls.DESCRIPTION)
        for key, kwargs in cls.ARGS.items():
            env, arg = key
            default = getenv(env)
            if default is not None:
                nargs = kwargs.get('nargs')
                if nargs not in ('?', None):
                    default = default.split()
                kwargs['default'] = default
            parser.add_argument(arg, **kwargs)
        return parser.parse_args(argv)

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch cfg from args."""
        raise NotImplementedError()  # pragma: no cover


class NomadScheduled(Micro):  # pylint: disable=abstract-method
    """Nomad scheduled micro."""

    @classmethod
    def run_once_now(cls) -> None:
        """Run once now."""
        i = cls.from_argv(sys_argv[1:])
        i.run()

    @classmethod
    def run_ping_now(cls) -> None:
        """Run ping now."""
        i = cls.from_argv(sys_argv[1:])
        i.ping()

    def __init__(
            self,
            input,  # pylint: disable=redefined-builtin
            output,
            model) -> None:
        """Initialize microservice."""
        self.input = input
        self.output = output
        self.model = model

    def ping(self) -> None:
        """Ping."""
        assert self.output.ping(), 'Output did not ping.'
        assert self.input.ping(), 'Input did not ping.'

    def run(self) -> None:
        """Run the model."""
        self.ping()
        self.model(self.input, self.output)
