#!/usr/bin/env python3
"""
Everskies API Wrapper
"""

__title__ = 'everskies'
__author__ = 'EthanHindmarsh'
__license__ = 'MIT'
__version__ = "0.0.11a"

__path__ = __import__('pkgutil').extend_path(__path__, __name__)

import logging
from collections import namedtuple

from .user import *
from .forum import *
from .token import *
from . import utils, errors

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=0, minor=0, micro=11, releaselevel='alpha', serial=0)

logging.getLogger(__name__).addHandler(logging.NullHandler())
