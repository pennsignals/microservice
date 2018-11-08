"""Core."""

from argparse import (
    ArgumentParser,
    Namespace,
)
from datetime import datetime
from functools import wraps
from pickle import load
from gc import collect
import logging
from os import getenv
from sys import (
    argv as sys_argv,
    stdout,
)
from time import sleep as block

from schedule import (
    every,
    next_run,
    run_pending,
)
from yaml import safe_load as yaml_loads


CONNECT = True
BACKOFF = 0.15
ENCODING = 'utf-8'
RETRIES = 5
TZ_AWARE = True


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


class Configurable:
    """Configurable."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        raise NotImplementedError()

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        pass


class Microservice:
    """Microservice."""

    ARGS = {}
    DESCRIPTION = 'Microservice'

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
    def from_argv(cls, argv) -> object:
        """Return microservice from command line and environment variables."""
        return cls.from_cfg(cls.cfg_from_args(cls.parse_args(argv)))

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return microservice from cfg."""
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def main(cls):
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
        raise NotImplementedError()


class Scheduled(Microservice):  # pylint: disable=abstract-method
    """Scheduled microservice."""

    @classmethod
    def run_once_now(cls) -> None:
        """Run once now."""
        i = cls.from_argv(sys_argv[1:])
        i.run()

    @classmethod
    def run_on_schedule(cls) -> None:
        """Run on schedule."""
        i = cls.from_argv(sys_argv[1:])
        every().day.at(i.scheduled_time).do(i.run)
        i()

    def __init__(
            self,
            input, output, model,
            scheduled_time: str,
            resolution: float):
        # pylint: disable=too-many-arguments,redefined-builtin
        """Initialize microservice."""
        self.input = input
        self.output = output
        self.model = model
        self.scheduled_time = scheduled_time
        self.resolution = resolution

    def __call__(self) -> None:
        """Run microservice."""
        old_value = None

        self.output.ping()
        self.input.ping()

        while True:
            run_pending()
            new_value = next_run()
            now = datetime.now()
            interval = max(
                self.resolution,
                (new_value - now).total_seconds() * 0.5)
            if old_value != new_value:
                logger.info(
                    'Next scheduled run: %s, initial sleep interval is %s',
                    new_value, interval)
                old_value = new_value
            block(interval)

    def run(self) -> None:
        """Run the model."""
        raise NotImplementedError()  # pragma: no cover


class Intervaled(Microservice):
    """Intervaled microservice."""

    # pylint: disable=abstract-method,too-few-public-methods
    pass
