"""Example Mssql Input."""

from __future__ import annotations

from argparse import Namespace

from yaml import safe_load as yaml_loads

from .mssql import Input as BaseInput, retry_on_operational_error


class Input(BaseInput):
    """Input.

    Delete; or customize, rename, this class/file.

    Import and use the @retry_on_operational_error to handle mssql disconnect
    for atomic units of work.
    """

    ARGS = {
        ("INPUT_URI", "--input-uri"): {
            "dest": "input_uri",
            "help": "Mssql input uri.",
            "type": str,
        },
        ("INPUT_TABLES", "--input-tables"): {
            "dest": "input_tables",
            "help": "Yaml configuration file of tables.",
            "type": str,
        },
    }

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> None:
        """Patch args into cfg."""
        for key, value in (("uri", args.input_uri),):
            if value is not None:
                cfg[key] = value

        for key, value in (("tables", args.input_tables),):
            if value is not None:
                with open(value) as fin:
                    cfg[key] = yaml_loads(fin.read())
        return cfg

    @retry_on_operational_error()
    def __call__(self):
        raise NotImplementedError()
