"""Service."""

from __future__ import annotations

import logging
from argparse import ArgumentParser, Namespace
from functools import wraps
from gc import collect
from os import getenv
from pickle import load
from sys import argv as sys_argv
from sys import stdout

from yaml import safe_load as yaml_loads

from .configurable import Configurable

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
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
    with open(file_name, "rb") as fin:
        return load(fin)


class Service(Configurable):
    """Service."""

    CONFIGURATION = {
        ("CONFIGURATION", "--cfg"): {
            "dest": "configuration",
            "help": "Yaml file for configuration.",
            "type": str,
        }
    }

    ARGS = {**CONFIGURATION}

    DESCRIPTION = "Service"

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
    def from_argv(cls, argv) -> Service:
        """Return instance from command line and environment variables."""
        return cls.from_cfg(cls.cfg_from_args(cls.parse_args(argv)))

    @classmethod
    def from_cfg(cls, cfg: dict) -> Service:
        """Return instance from cfg."""
        raise NotImplementedError()  # pragma: no cover

    @classmethod
    def main(cls) -> None:
        """Main.

        See setup.py entry point.
        """
        i = cls.from_argv(sys_argv[1:])
        i()

    @classmethod
    def main_ping(cls) -> None:
        """Main ping.

        See setup.py entry_point.
        """
        i = cls.from_argv(sys_argv[1:])
        i.ping()

    @classmethod
    def parse_args(cls, argv: list) -> Namespace:
        """Return parsed args from command line and environment variables."""
        parser = ArgumentParser(description=cls.DESCRIPTION)
        for key, kwargs in cls.ARGS.items():
            env, arg = key
            default = getenv(env)
            if default is not None:
                nargs = kwargs.get("nargs")
                if nargs not in ("?", None):
                    default = default.split()
                kwargs["default"] = default
            parser.add_argument(arg, **kwargs)
        return parser.parse_args(argv)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        raise NotImplementedError()  # pragma: no cover

    def __call__(self):
        """Run."""
        raise NotImplementedError()

    def ping(self):
        """Ping."""
        raise NotImplementedError()


class SimpleService(Service):  # pylint: disable=abstract-method
    """SimpleService.

    Extend this class for your own service and implement
        ARGS, from_cfg, and patch_args which require your
        own Model, Inputs, Outputs, *Input, and *Output classes.

    from .service import Service as BaseService

    class Service(BaseService):
        ...

    Focus on input and output designation leads to the ability to
        read production datasources and write to development datasinks
        even though the input and output would typically point at the
        same database when the service is deployed.

    Focus on separating the code model code from inputs and outputs
        leads to the ability to modify these independently.

    Services are responsible for drawing and documenting
        strong Data Models with ERD, and DFD) for each output.
        json, yaml, xml, mongo documents without classes/types/metadata
        are not strong Data Models.
    """

    def __init__(self, inputs, outputs, model) -> None:
        """Init."""
        self.inputs = inputs
        self.outputs = outputs
        self.model = model

    def ping(self) -> None:
        """Ping.

        Throw an unhandled exception when configuration, dependencies,
            or secrets are wrong or an upstream/downstream component
            is unavailable.
        """
        self.model.ping()
        self.outputs.ping()
        self.inputs.ping()

    def __call__(self) -> None:
        """Run.

        Delegate to ping and then run the model.
        """
        self.ping()
        self.model(self.inputs, self.outputs)
