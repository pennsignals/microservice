"""Input."""

from __future__ import annotations
from argparse import Namespace
from logging import (
    basicConfig,
    getLogger,
    INFO,
)
from sys import stdout

from yaml import safe_load as yaml_loads

from .mssql import (
    Input as BaseMssqlInput,
    # retry_on_operational_error,
)


basicConfig(
    level=INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=stdout)
logger = getLogger(__name__)


class Input(BaseMssqlInput):
    """Input."""

    ARGS = {
        ('INPUT_URI', '-input-uri'): {
            'dest': 'input_uri',
            'help': 'Mssql input uri.',
            'type': str,
        },
        ('INPUT_TABLES', '-input-tables'): {
            'dest': 'input_tables',
            'help': 'Yaml configuration file of tables.',
            'type': str,
        },
    }

    @classmethod
    def patch_args(cls, cfg: dict, args: Namespace) -> None:
        """Patch args into cfg."""
        for key, value in (
                ('uri', args.input_uri),):
            if value is not None:
                cfg[key] = value

        for key, value in (
                ('tables', args.input_tables),):
            if value is not None:
                with open(value) as fin:
                    cfg[key] = yaml_loads(fin.read())

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
