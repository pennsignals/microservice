"""Project."""

from __future__ import annotations

from argparse import Namespace
from logging import INFO, basicConfig, getLogger
from sys import stdout

from setuptools_scm import get_version

from .example_inputs import Inputs
from .example_outputs import Outputs
from .model import Model
from .service import SimpleService as BaseService

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)


__version__ = get_version(root="../..", relative_to=__file__)


class Service(BaseService):
    """Service."""

    DESCRIPTION = "Describe your microservice here."

    ARGS = {**BaseService.ARGS, **Inputs.ARGS, **Outputs.ARGS}

    @classmethod
    def from_cfg(cls, cfg: dict) -> Service:
        """Return microservice from cfg."""
        kwargs = {
            key: from_cfg(cfg[key])
            for key, from_cfg in (
                ("inputs", Inputs.from_cfg),
                ("outputs", Outputs.from_cfg),
                ("model", Model.from_cfg),
            )
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        for key, patch_args in (
            ("inputs", Inputs.patch_args),
            ("outputs", Outputs.patch_args),
            ("model", Model.patch_args),
        ):
            cfg[key] = patch_args(args, cfg.get(key))
        return cfg
