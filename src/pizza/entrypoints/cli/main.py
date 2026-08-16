"""The interactive client, and the process that holds it.

It composes and nothing else: the configuration is read, one connection to the API
is opened, and the loop is handed both. Every screen, every call and every failure
belongs to the modules beside this one.

The configuration is read first, so a missing or malformed value is one line on
standard error rather than a traceback from somewhere further in.
"""

import os
import sys

from pizza.config import ConfigurationError, load_client_settings
from pizza.entrypoints.cli.client import ApiClient
from pizza.entrypoints.cli.menu import run_menu


def main() -> None:
    try:
        settings = load_client_settings(os.environ)
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    with ApiClient(settings.api_base_url) as api:
        run_menu(api)


if __name__ == "__main__":
    main()
