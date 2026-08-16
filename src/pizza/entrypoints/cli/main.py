"""Composition root of the interactive CLI.

It reads the configuration, opens one connection to the API and hands it to the menu
loop. Screens, calls and failure handling belong to the modules beside this one.

The configuration is read first, so a missing or malformed value produces one line on
standard error rather than a traceback from further in.
"""

import os
import sys

from pizza.config import ConfigurationError, load_client_settings
from pizza.entrypoints.cli.client import ApiClient
from pizza.entrypoints.cli.menu import run_menu


def main() -> None:
    """Run the interactive menu until the user exits."""
    try:
        settings = load_client_settings(os.environ)
    except ConfigurationError as error:
        print(error, file=sys.stderr)
        raise SystemExit(1) from error

    with ApiClient(settings.api_base_url) as api:
        run_menu(api)


if __name__ == "__main__":
    main()
