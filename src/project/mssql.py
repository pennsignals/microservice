"""Mssql."""

from __future__ import annotations

import re
from contextlib import contextmanager
from functools import wraps
from logging import INFO, basicConfig, getLogger
from sys import stdout
from time import sleep as block
from urllib.parse import parse_qsl, unquote

from pandas import DataFrame

# pylint: disable=no-name-in-module
from pymssql import DatabaseError, InterfaceError, OperationalError
from pymssql import connect as MssqlConnection

from .configurable import Configurable
from .constants import BACKOFF, RETRIES

basicConfig(
    level=INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=stdout,
)
logger = getLogger(__name__)  # pylint: disable=invalid-name


def retry_on_operational_error(retries=RETRIES, backoff=BACKOFF):
    """Retry decorator for OperationalErrors.

    Use this decorator to make operations resilient to db failure.
    """

    def wrapper(func):
        """Return wrapped method."""

        @wraps(func)
        def wrapped(*args, **kwargs):
            """Return method result."""
            try:
                return func(*args, **kwargs)
            except OperationalError as retry:
                logger.exception(retry)
                for i in range(retries):
                    try:
                        return func(*args, **kwargs)
                    except OperationalError:
                        block(backoff * i)
                raise

        return wrapped

    return wrapper


class Uri(
    Configurable
):  # noqa: E501; pylint: disable=too-many-instance-attributes,abstract-method,line-too-long
    """Uri."""

    URI = re.compile(
        (
            r"mssql://"
            r"(?:"
            r"(?P<username>[^:@/]*)(?::(?P<password>[^@/]*))?"
            r"@)?"
            r"(?:"
            r"(?:\[(?P<ipv6host>[^\]]+)\]"
            r"|"
            r"(?P<ipv4host>[^/:]+)"
            r")?"
            r"(?::(?P<port>[^/]*))?"
            r")?"
            r"(?:/(?P<database>.*))?"
        )
    )

    @classmethod
    def _from_qsl(cls, in_kwargs, out_kwargs):
        query = {}
        for key, value in in_kwargs:
            entry = query.get(key, None)
            if entry is None:
                query[key] = value
            elif isinstance(entry, list):
                entry.append(value)
            else:
                query[key] = [entry, value]

        for key, cast in (
            ("timeout", int),
            ("login_timeout", int),
            ("charset", str),
            ("as_dict", bool),
            ("appname", str),
            ("conn_properties", str),
            ("autocommit", bool),
            ("tds_version", str),
        ):
            value = query.get(key, None)
            if value is not None:
                out_kwargs[key] = cast(unquote(value))

    @classmethod
    def from_cfg(cls, cfg: str) -> Uri:
        """Return instance from uri."""
        match = Uri.URI.match(cfg)
        if match is None:
            logger.info(cfg)
            raise ValueError("Invalid mssql uri")
        kwargs = match.groupdict()
        if kwargs["database"] is not None:
            tokens = kwargs["database"].split("?", 2)
            kwargs["database"] = tokens[0]

            if len(tokens) > 1:
                cls._from_qsl(parse_qsl(tokens[1]), kwargs)

        for key, cast in (
            ("username", str),
            ("password", str),
            ("database", str),
            ("ipv4host", str),
            ("ipv6host", str),
            ("port", int),
        ):
            value = kwargs.get(key, None)
            if value is not None:
                kwargs[key] = cast(unquote(value))

        ipv4_host, ipv6_host = (
            kwargs.pop(key) for key in ("ipv4host", "ipv6host")
        )
        kwargs["host"] = ipv4_host or ipv6_host

        return cls(**kwargs)

    def __init__(  # pylint: disable=too-many-arguments,too-many-locals
        self,
        host: str = "",
        username: str = None,
        password: str = None,
        database: str = "",
        timeout: int = 0,
        login_timeout: int = 0,
        charset: str = "UTF-8",
        as_dict: bool = False,
        appname: str = "",
        port: int = 1433,
        conn_properties: str = None,
        autocommit: bool = False,
        tds_version: str = None,
    ) -> object:
        """Initialize mssql uri."""
        if charset is None:
            charset = "UTF-8"
        if port is None:
            port = 1433
        if tds_version is None:
            tds_version = "7.3"
        self.host = host
        self.username = username
        self.password = password
        self.database = database
        self.timeout = timeout
        self.login_timeout = login_timeout
        self.charset = charset
        self.as_dict = as_dict
        self.appname = appname
        self.port = port
        self.conn_properties = conn_properties
        self.autocommit = autocommit
        self.tds_version = tds_version

    @contextmanager
    def connection(self):
        """Mssql connection contextmanager."""
        with MssqlConnection(
            host=self.host,
            user=self.username,
            password=self.password,
            port=self.port,
            database=self.database,
            timeout=self.timeout,
            login_timeout=self.login_timeout,
            charset=self.charset,
            as_dict=self.as_dict,
            appname=self.appname,
            conn_properties=self.conn_properties,
            autocommit=self.autocommit,
            tds_version=self.tds_version,
        ) as connection:
            try:
                logger.info('{"mssql": "open"}')
                yield connection
            finally:
                logger.info('{"mssql": "close"}')

    @contextmanager
    def commit(self):
        """Uri commit contextmanager."""
        with self.connection() as connection:
            try:
                with connection.cursor() as cursor:
                    yield cursor
                connection.commit()
            except BaseException:
                connection.rollback()
                raise

    @contextmanager
    def rollback(self):
        """Uri rollback contextmanager."""
        with self.connection() as connection:
            try:
                with connection.cursor() as cursor:
                    yield cursor
            finally:
                connection.rollback()

    @retry_on_operational_error()
    def ping(self, cursor) -> bool:
        """Ping."""  # pylint: disable=no-self-use
        cursor.execute("""select 1 as n""")
        for _ in cursor.fetchall():
            return True
        return False


class Input(Configurable):  # pylint: disable=abstract-method
    """Input."""

    @classmethod
    def from_cfg(cls, cfg: dict) -> object:
        """Return input from cfg."""
        kwargs = {
            key: from_cfg(cfg[key])
            for key, from_cfg in (("tables", list), ("uri", Uri.from_cfg))
        }
        return cls(**kwargs)

    @classmethod
    def query_to_df(cls, cursor, query, params=None) -> DataFrame:
        """Query to dataframe."""
        cursor.execute(query, params)
        columns = (each[0] for each in cursor.description)
        df = DataFrame(cursor.fetchall())
        if df.empty:
            df = DataFrame(columns=columns)
        else:
            df.columns = columns
        return df

    def __init__(self, uri: Uri, tables: list) -> None:
        """Initialize input."""
        self.uri = uri
        self.tables = tables

    @contextmanager
    def rollback(self) -> None:
        """Connect contextmanager."""
        with self.uri.rollback() as cursor:
            yield cursor

    def ping(self) -> bool:
        """Ping mssql on startup."""
        with self.uri.rollback() as cursor:
            return self.uri.ping(cursor) and self.select_from_tables(cursor)

    @retry_on_operational_error()
    def select_from_tables(self, cursor) -> bool:
        """Select."""
        failures = []
        for each in self.tables:
            try:
                sql = """
select 1 as n where exists (select 1 as n from %s)""" % (
                    each,
                )
                cursor.execute(sql)
                for _ in cursor.fetchall():
                    pass
            except (DatabaseError, InterfaceError) as e:
                logger.warning(e)
                logger.warning(sql)
                number, *_ = e.args
                if number == 230:  # column privileges
                    continue
                failures.append(each)
        return not bool(failures)
