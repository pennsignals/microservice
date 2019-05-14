"""Model."""

from __future__ import annotations
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
import pickle
from sys import stdout

from .configurable import Configurable
from .micro import garbage_collection


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


def unpickle_from_file(file_name):
    """Return unpickle from file."""
    with open(file_name, 'rb') as f:
        return pickle.load(f)


class Model(Configurable):
    """Model."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        kwargs = {
            key: cast(cfg[key])
            for key, cast in (
                ('first_model_configurable_property', int),
                ('second_model_configurable_property', float),
            )
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, cfg: dict, args) -> None:
        """Patch cfg from args."""
        # pylint: disable=abstract-method

    @garbage_collection
    def __call__(
            self,
            input,  # pylint: disable=redefined-builtin
            output):
        """Run model."""
        idfs = input()
        tdfs = self.transform(*idfs)
        pdfs = self.predict(*tdfs)
        output(idfs, pdfs)  # allow idfs to be tracked with their pdfs

    def transform(self, *idfs) -> tuple:
        """Transform."""
        raise NotImplementedError()

    def predict(self, *tdfs) -> tuple:
        """Predict."""
        raise NotImplementedError()
