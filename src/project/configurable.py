"""Configurable."""

from __future__ import annotations
from argparse import Namespace


class Configurable:
    """Configurable."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> Configurable:
        """Return model from cfg."""
        raise NotImplementedError()

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        raise NotImplementedError()
