"""Example Mongo Input."""

from argparse import Namespace

from .mongo import Mongo as BaseInput, retry_on_reconnect


class Input(BaseInput):
    """Input.

    Delete; or customize, rename, and extract this class to another file.
    """

    ARGS = {
        ("INPUT_URI", "--input-uri"): {
            "dest": "input_uri",
            "help": "Mongo input uri.",
            "type": str,
        }
    }

    @classmethod
    def patch_args(cls, args: Namespace, cfg: dict) -> dict:
        """Patch args into cfg."""
        if cfg is None:
            cfg = {}

        for key, *values in (("uri", args.input_uri, args.mongo_uri),):
            for value in values:
                if value is not None:
                    cfg[key] = value
                    break
        return cfg

    @retry_on_reconnect()
    def __call__(self):
        raise NotImplementedError()
