"""ExampleOutputs."""

from __future__ import annotations

from argparse import Namespace

from .configurable import Configurable
from .example_mongo_output import Output as MongoOutput


class Outputs(Configurable):
    """Outputs.

    Rename and revise this file to patch, configure, and initialize
        your own outputs.

    Delegate work from your model to outputs to avoid coupling your model
        to changing operational aspects (business rules).

    An example of an output pipeline that hides details (business rules)
        from your model.

    def __call__(self, batch) -> None:
        self.twilio(batch)
        self.slack(batch)
        self.mongo(batch)
        self.zmq(batch)
    """

    ARGS = {**MongoOutput.ARGS}

    @classmethod
    def from_cfg(cls, cfg: dict) -> Outputs:
        """Return instance from cfg."""
        kwargs = {
            from_cfg(cfg[key])
            for key, from_cfg in (("mongo", MongoOutput.from_cfg),)
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        if cfg is None:
            cfg = {}
        for key, patch_args in (("mongo", MongoOutput.patch_args),):
            cfg[key] = patch_args(args, cfg.get(key))
        return cfg
