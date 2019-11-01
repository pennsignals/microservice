"""Output."""

from __future__ import annotations

from argparse import Namespace
from logging import INFO, basicConfig, getLogger
from sys import stdout

from .mongo import Mongo as BaseOutput  # retry_on_reconnect,

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)


class Output(BaseOutput):
    """Output."""

    ARGS = {
        ("OUTPUT_URI", "-output-uri"): {
            "dest": "output_uri",
            "help": "Mongo output uri.",
            "type": str,
        }
    }

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        if cfg is None:
            cfg = {}
        for key, value in (
            ("uri", args.output_uri),
        ):  # match 'dest' in OUTPUT_URI
            if value is not None:
                cfg[key] = value
        return cfg

    def __call__(self, batch) -> None:
        """Write output.

        Modify this method.
        Accept whatever additional arguments you need.

        Wrap unit of work methods with retry_on_reconnect decorator.
        """
        # transform = batch.transform
        # evidence = batch.evidence
        # with self.collections() as collections:
        #    self.write_evidence(collections.evidence, evidence_batch)
        #    self.write_transform(collections.evidence, transform_batch)
        #    self.write_prediction(collections.prediction, prediction_batch)
        raise NotImplementedError()

    def ping(self) -> bool:
        """Ping output.

        Ensure that the output is online.
        Aquire any startup state needed here:
            max_batch_id, last_inserted_date, etc.
        It is ok to read from outputs to get last output state,
            but not data for features, or cohort.
        """
        raise NotImplementedError()

    # @retry_on_reconnect()
    # def write_prediction(self, collection, df) -> None:
    #     collection.insert_many(df)
