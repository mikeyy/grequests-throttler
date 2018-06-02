#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Meta data for grequests-throttler."""

import logging

__author__ = """Michael Mooney"""
__email__ = 'mikeyy@mikeyy.com'
__version__ = '0.0.1'
__base_nonocap_version__ = 'v1.0.0'

# Setup root logger
_logger = logging.getLogger('throttler')
_log_handler = logging.StreamHandler()
_fmt = '[{levelname[0]}:{name}] {msg}'
_formatter = logging.Formatter(fmt=_fmt, style='{')
_log_handler.setFormatter(_formatter)
_log_handler.setLevel(logging.DEBUG)
_logger.addHandler(_log_handler)
_logger.propagate = False
# logger.setLevel(logging.DEBUG)

version = __version__
version_info = tuple(int(i) for i in version.split('.'))

__all__ = [
    'version',
    'version_info',
]
