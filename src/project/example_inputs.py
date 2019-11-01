"""ExampleInputs."""

from __future__ import annotations

from argparse import Namespace

from .configurable import Configurable
from .example_mongo_input import Input as MongoInput
from .example_mssql_input import Input as MssqlInput


class InputBatch:  # pylint: disable=too-few-public-methods
    """InputBatch"""

    def __init__(self):
        """Add named parameters, likely these are sanitized dfs."""
        raise NotImplementedError()


class Inputs(Configurable):
    """Inputs.

    Rename and revise this file to patch, configure, and initialize
        your own inputs.

    """

    ARGS = {**MongoInput.ARGS, **MssqlInput.ARGS}

    @classmethod
    def from_cfg(cls, cfg: dict) -> Inputs:
        """Return instance from cfg."""
        kwargs = {
            from_cfg(cfg[key])
            for key, from_cfg in (
                ("mongo", MongoInput.from_cfg),
                ("mssql", MssqlInput.from_cfg),
            )
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        if cfg is None:
            cfg = {}
        for key, patch_args in (
            ("mongo", MongoInput.patch_args),
            ("mssql", MssqlInput.patch_args),
        ):
            cfg[key] = patch_args(args, cfg.get(key))
        return cfg

    def __init__(self):
        """Init.
        Add configurable parameters used across all inputs to the this.
        For example, the length of a lookback window might be shared
            across Inputs.

        Add configurable parameters specific an input to the constructor
            of the input.
        For example a configurable mapping of names to features might be
            specific to an input.
        """
        raise NotImplementedError()

    def __call__(self):
        """__call__.

        Implement the __call__ method to collect all dataframes from
            your various inputs into a batch object or a namedtuple
            of dataframes.

        This could be an appropriate place to perform pre-transform data
            munging, to isolate these changes from your model.

        Add runtime parameters used across all inputs here.
        For example the replay status, and now parameters.

        Add runtime parameters used for a specific input to the __call__
            method of the input.
        For example the computed valid_on..valid_end for specific types of
            evidence of an input.
        """
        raise NotImplementedError()
