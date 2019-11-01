"""Model.

Alter this model instance to

"""

from __future__ import annotations

from argparse import Namespace
from logging import INFO, basicConfig, getLogger
from sys import stdout

from .configurable import Configurable
from .example_inputs import InputBatch
from .service import (
    # unpickle_from_file,
    garbage_collection,
)

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)


class TransformBatch:  # pylint: disable=too-few-public-methods
    """TransformBatch."""

    def __init__(self, batch: InputBatch):
        """Add parameters and properties to accumulate work."""
        self.provenance = batch


class PreditionBatch:  # pylint: disable=too-few-public-methods
    """Predictions."""

    def __init__(self, batch: TransformBatch):
        """Add parameters and properties to accumulate work."""
        self.provenance = batch


class Model(Configurable):
    """Model."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        kwargs = {
            key: from_cfg(cfg[key])
            for key, from_cfg in (
                ("first_model_configurable_property", int),
                ("second_model_configurable_property", float),
            )
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        return cfg

    @garbage_collection
    def __call__(self, inputs, outputs):
        """Run model."""
        batch = inputs()
        #  batch = self.transform(batch), if inputs doesn't perform transform
        batch = self.predict(batch)
        outputs(batch)

    def transform(self, batch) -> object:
        """Transform.

        Return Transforms with a source for provenance.
        """
        raise NotImplementedError()

    def predict(self, batch) -> object:
        """Predict.

        Return Predictions with a provenance
        """
        raise NotImplementedError()
