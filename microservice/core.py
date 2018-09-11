"""Core."""

from argparse import ArgumentParser
from gc import collect
import logging

from yaml import safe_load as yaml_loads


CONNECT = True
BACKOFF = 0.15
ENCODING = 'utf-8'
RETRIES = 5
TZ_AWARE = True


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
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


class Microservice:

    ARGS = {}
    DESCRIPTION = 'Microservice'

    @classmethod
    def cfg_from_args(cls, args):
        """Return cfg from args."""
        key = args.configuration
        assert key is not None

        with open(key) as fin:
            return yaml_loads(fin.read())

    @classmethod
    def from_argv(cls, argv):
        """Return an object from command line and environment variables."""
        return cls.from_cfg(cls.cfg_from_args(cls.parse_args(argv)))

    @classmethod
    def from_cfg(cls, cfg):
        """Return an object from cfg."""
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def parse_args(cls, argv):
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
