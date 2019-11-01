"""Mongo."""

from __future__ import annotations

from argparse import Namespace
from collections import namedtuple
from contextlib import contextmanager
from functools import wraps
from logging import INFO, basicConfig, getLogger
from sys import stdout
from time import sleep as block
from uuid import uuid4

from pymongo import MongoClient
from pymongo.errors import AutoReconnect

from .configurable import Configurable
from .constants import BACKOFF, RETRIES

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)  # pylint: disable=invalid-name


def retry_on_reconnect(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for AutoReconnect.

    The pymongo client does not retry operations even when
        mongo reports auto reconnect is available.

    Use this decorator to make operations resilient to db failure or failover.

    Ideally wrap methods of your mongo input and output classes
        as unit of work.

    from .mongo import Mongo as Baseinput

    class Myinput(BaseInput):
        ...

        @retry_on_reconnect()
        def get_labs(
                self,
                patient_ids: set,
                names: set,
                valid_on: int,  # epoch ms
                valid_end: int,  # epoch ms
        ) -> DataFrame:
            with self.collections() as collections:
                return self.bson_to_df(
                    collections.labs.find({
                        'patient_id': {
                            '$in': list(patient_ids),
                        },
                        'name': {
                            '$in': list(names),
                        },
                        'valid_on': {
                            '$gte': valid_on,
                            '$lt': valid_end,
                        }
                    }).sort({
                        '_id': -1,
                    })
                )
    """

    def wrapper(func):
        """Return wrapped method."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            """Return method result."""
            try:
                return func(*args, **kwargs)
            # coverage only with a replicaset and failover.
            except AutoReconnect as retry:
                logger.exception(retry)
                for i in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except AutoReconnect:
                        block(backoff * i)
                raise

        return wrapped

    return wrapper


class Mongo(Configurable):
    """Mongo.

    Extend this class for your own project as an Input or Output.
    Implement ARGS, patch_args, and ping.

    from .mongo import Mongo as BaseOutput

    class MyOutput(BaseOutput):
        '''Do not name your class MyOutput.'''
        ...

    from .mongo import Mongo as BaseInput

    class SignalsInput(BaseInput):
        '''SignalsInput.'''
        ...

    Add methods to your derived class that should do most of the
        serialization and deserialization work.
    Likely accept batch, dataframe, list or dictionary-like parameters
        to be serialized (Output) or named query parameters (Input).
    These methods should help document the code and remove complexity from
        the model or other component that uses them.

    Pull up common general purpose serialization/deserialization here:
        df_to_bsonable
        bson_to_df --import Dataframe within try/except to avoid making
            all projects require pandas
        list_to_bson
        dict_to_bson
    """

    @classmethod
    def from_cfg(cls, cfg: dict) -> Mongo:
        """Return model from cfg."""
        collections = cfg["collections"]
        collections_cls_name = "_Collections" + uuid4().hex

        class Collections(
            namedtuple(  # pylint: disable=too-few-public-methods
                collections_cls_name, collections.keys()
            )
        ):  # pylint: disable=too-few-public-methods
            """Collections."""

            @classmethod
            def from_cfg(cls, cfg: dict) -> object:
                """Return collections from cfg."""
                return cls(**cfg)

        kwargs = {
            key: from_cfg(cfg[key])
            for key, from_cfg in (
                ("uri", str),
                ("collections", Collections.from_cfg),
            )
        }
        return cls(**kwargs)

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg, return cfg."""
        raise NotImplementedError()

    def __init__(self, uri: str, collections: namedtuple) -> None:
        """Initialize Mongo."""
        self.uri = uri
        self._collections = collections

    @contextmanager
    def collections(self) -> None:
        """Contextmanager for collections.

        with signals.collections() as collections:
            collections.flowsheets.find(...)

        with my_output.collections() as collections:
            collections.predictions.insertMany(...)

        The property/collection identifiers ('batches', 'predictions')
            are mapped to the actual mongo collection names
            in the configuration file.
        """
        with self.database() as database:
            kwargs = {
                key: database[value]
                for key, value in self._collections._asdict().items()
            }
            yield self._collections.__class__(**kwargs)

    @contextmanager
    def connection(self) -> None:
        """Contextmanager for connection.

        Authentication is handled transparently by the
            MongoClient with a uri.
        """
        with MongoClient(self.uri) as connection:
            logger.info('{"mongo": "open"}')
            try:
                yield connection
            finally:
                logger.info('{"mongo": "close"}')

    @contextmanager
    def database(self) -> None:
        """Contextmanager for database.

        Selecting the configurable default database is handled
            transparently by the MongoClient with a uri.
        """
        with self.connection() as connection:
            database = connection.get_database()
            logger.info('{"mongo.open": {"database": "%s"}}', database.name)
            try:
                yield database
            finally:
                logger.info(
                    '{"mongo.closed": {"database": "%s"}}', database.name
                )

    def ping(self) -> bool:
        """Ping mongo on startup.

        Revise this default implementations to get mongo metadata
            from the server.
        Force the connection to open and close on ping validating
            the uri connection string/secrets/configuration.
        """
        raise NotImplementedError()
