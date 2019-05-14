"""Project."""

from __future__ import annotations
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from sys import stdout

from .micro import NomadScheduled as BaseMicro
from .input import Input
from .output import Output
from .model import Model


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


class Micro(BaseMicro):
    """Micro."""

    DESCRIPTION = 'Describe your microservice here.'

    ARGS = {
        **BaseMicro.ARGS,
        **Input.ARGS,
        **Output.ARGS,
    }

    @classmethod
    def from_cfg(cls, cfg: dict) -> Micro:
        """Return microservice from cfg."""
        kwargs = {
            key: cast(cfg[key])
            for key, cast in (
                ('input', Input.from_cfg),
                ('output', Output.from_cfg),
                ('model', Model.from_cfg))}
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, cfg: dict, args) -> None:
        """Patch cfg from args."""
        for key, patch_args in (
                ('input', Input.patch_args),
                ('output', Output.patch_args),
                ('model', Model.patch_args)):
            entry = cfg.get(key)
            if entry is None:
                entry = cfg[key] = {}
            patch_args(entry, args)
