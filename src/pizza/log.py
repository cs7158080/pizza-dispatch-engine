"""One log format, for every process the system starts.

Both composition roots call this, so a line from the api and a line from the
worker are read the same way. It sits beside config.py rather than in a layer:
it is neither core nor adapter.
"""

import logging

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


def configure_logging(level: str) -> None:
    """Install the root handler both services log through.

    Called first thing in a composition root, and once: basicConfig does nothing
    if the root logger already has a handler.

    `pika` is raised to WARNING because it narrates a successful publish and a
    successful reconnect at INFO, several lines each. Its own errors still print.
    """
    logging.basicConfig(level=level, format=_FORMAT)
    logging.getLogger("pika").setLevel(logging.WARNING)
