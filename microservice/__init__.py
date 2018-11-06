"""Microservice."""

from argparse import Namespace
from collections import namedtuple
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from sys import stdout
from uuid import uuid4

from .core import (
    Configurable,
    garbage_collection,
    Scheduled as BaseMicroservice,  # --or-- Intervaled as BaseMicroservice
)
from .mongo import (
    Mongo,
    retry_on_reconnect,  # pylint: disable=unused-import
)
from .mssql import (
    Mssql,
    retry_on_operational_error,  # pylint: disable=unused-import
)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


class Input(Mssql):
    """Mssql Input."""

    INPUT_DSN = {
        ('INPUT_DSN', '-input-dsn'): {
            'dest': 'input_dsn',
            'help': 'Mssql input dsn (server, username, password, database).',
            'nargs': 4,
            'type': str,
        },
    }

    ARGS = {
        **INPUT_DSN,
    }

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        raise NotImplementedError()

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        for key, value in (
                ('dsn', args.input_dsn),):  # match 'dest' in INPUT_DSN
            if value != '':
                cfg[key] = value

    def __call__(self) -> tuple:
        """Return a tuple of input dfs.

        Modify this method.
        Accept whatever additional arguments you need.
        Perhaps return a namedtuple and update the method signature
          if you have more than ~5 dfs
        Perhaps accept monotinically increasing id intervals
            (from_id, to_id) for replayability.
          See monitor for an example.
        """
        #   with self.rollback() as cursor:
        #     idf1 = self.get_idf1(cursor)
        #     idf2 = self.get_idf2(cursor)
        #     return idf1, idf2
        raise NotImplementedError()

    # retry_on_operational_error()
    # def get_df1(cursor) -> DataFrame:
        # """Get df1."""
        # cursor.execute('''select 1 as n''')
        # return DataFrame(cursor.fetchAll())
        # raise NotImplementedError()

    def ping(self) -> None:
        """Ping input.

        Modify this method.
        Ensure that the input is online.
        Perhaps check to see if the mssql database has the expected
            tables and stored procedure.
          See ping in vent-notify-mssql example.
        Set any startup state needed here:
            max_batch_id, last_inserted_date, etc.
        """
        raise NotImplementedError()


class Output(Mongo):
    """Output."""

    OUTPUT_URI = {
        ('OUTPUT_URI', '-output-uri'): {
            'dest': 'output_uri',
            'help': 'Mongo output uri.',
            'type': str,
        },
    }

    ARGS = {
        **OUTPUT_URI,
    }

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        collection_map = cfg['collection_map']
        collection_map_cls_name = '_CollectionMap' + uuid4().hex
        collection_map_cls = namedtuple(
            collection_map_cls_name, collection_map.keys())
        kwargs = {
            key: cast(cfg[key])
            for key, cast in (
                ('uri', str),
                ('collection_map', collection_map_cls),
            )}
        kwargs['collection_map_cls'] = collection_map_cls
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        for key, value in (
                ('uri', args.output_uri),):  # match 'dest' in OUTPUT_URI
            if value != '':
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

    def ping(self) -> None:
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


class Model(Configurable):
    """Model."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return model from cfg."""
        return cls()

    @classmethod
    def patch_args(cls, cfg: dict, args) -> None:
        """Patch cfg from args."""
        pass

    @garbage_collection
    def __call__(self, input, output):  # pylint: disable=redefined-builtin
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


class Microservice(BaseMicroservice):
    """Microservice."""

    CONFIGURATION = {
        ('CONFIGURATION', '--cfg'): {
            'default': './local/configuration.cfg',
            'dest': 'configuration',
            'help': 'Yaml file for configuration.',
            'type': str,
        },
    }

    DESCRIPTION = 'Describe your microservice here.'

    ARGS = {
        **CONFIGURATION,
        **Input.ARGS,
        **Output.ARGS,
    }

    @classmethod
    def from_cfg(cls, cfg: dict):
        """Return microservice from cfg."""
        kwargs = {
            key: cast(cfg[key])
            for key, cast in (
                ('input', Input.from_cfg),
                ('output', Output.from_cfg),
                ('model', Model.from_cfg),
                ('resolution', float),
                ('scheduled_time', str))}
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, cfg: dict, args) -> None:
        """Patch cfg from args."""
        for key, patch_args in (
                ('input', Input.patch_args),
                ('output', Output.patch_args),
                ('model', Model.patch_args)):
            patch_args(cfg[key], args)

    def run(self) -> None:
        """Run the model."""
        self.model(self.input, self.output)
