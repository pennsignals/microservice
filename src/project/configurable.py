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
    def patch_args(cls, args: Namespace, cfg: dict) -> object:
        """Patch args into cfg, return cfg.

        Returned cfg is typically a dict.
        """
        raise NotImplementedError()
