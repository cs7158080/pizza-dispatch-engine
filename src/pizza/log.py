"""A single log format, shared by every process the system starts."""

import logging

_FORMAT = "%(asctime)s %(levelname)-8s %(name)s %(message)s"


def configure_logging(level: str) -> None:
    """Install the root log handler.

    Must be called once, at the start of a composition root: basicConfig does
    nothing if the root logger already has a handler.

    `pika` is raised to WARNING because it logs several lines per successful publish
    and reconnect at INFO. Its errors are still shown.
    """
    logging.basicConfig(level=level, format=_FORMAT)
    logging.getLogger("pika").setLevel(logging.WARNING)
