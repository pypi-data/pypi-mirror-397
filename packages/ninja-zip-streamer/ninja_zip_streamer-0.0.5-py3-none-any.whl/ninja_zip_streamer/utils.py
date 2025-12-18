"""Module containing helpers."""

import os
import logging
import requests


def get_logger_for(name: str) -> logging.Logger:
    """Get logger with appropriate name."""
    logging.basicConfig(
        format="%(levelname)s:%(message)s", level=os.environ.get("LOGLEVEL", "INFO")
    )
    logger = logging.getLogger(name)
    return logger


def get_session():
    """Get an HTTP(S) session."""
    sess = requests.Session()
    retries = requests.adapters.Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=[408, 410, 419, 421, 422, 424, 425, 429, 502, 503, 504, 505],
        allowed_methods=frozenset(["PUT", "POST", "GET"]),
    )
    adapter = requests.adapters.HTTPAdapter(max_retries=retries)
    sess.mount("http://", adapter=adapter)
    sess.mount("https://", adapter=adapter)
    return sess
