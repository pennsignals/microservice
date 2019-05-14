"""Output."""

from __future__ import annotations
from argparse import Namespace
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from sys import stdout

from .mongo import (
    Output as BaseMongoOutput,
    # retry_on_reconnect,
)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


class Output(BaseMongoOutput):
    """Output."""

    ARGS = {
        ('OUTPUT_URI', '-output-uri'): {
            'dest': 'output_uri',
            'help': 'Mongo output uri.',
            'type': str,
        },
    }

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        for key, value in (
                ('uri', args.output_uri),):  # match 'dest' in OUTPUT_URI
            if value is not None:
                cfg[key] = value

    def __call__(self, idfs: tuple, pdfs: tuple) -> None:
        """Emit output dfs.

        Modify this method.
        Accept whatever additional arguments you need.
        Perhaps accept namedtuples and update the method signature
        """
        # evidence, *idfs = idfs
        # prediction, *pfds = pdfs
        # with self.collection() as collection:
        #    self.write_evidence(collection.evidence, evidence)
        #    self.write_prediction(collection.prediction, prediction)
        raise NotImplementedError()

    def ping(self) -> bool:
        """Ping output.

        Ensure that the output is online.
        Aquire any startup state needed here:
            max_batch_id, last_inserted_date, etc.
        It is ok to read from outputs,
            but use a separate input if needed for local testing.
        """
        raise NotImplementedError()

    # @retry_on_reconnect()
    # def write_prediction(self, collection, df) -> None:
    #     collection.insert_many(df)
