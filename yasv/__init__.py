from .core import Field, Schema
from .validators import *

VERSION = (0, 1, 8, 'dev')
__version__ = '.'.join(map(str, VERSION[0:3])) + ''.join(VERSION[3:])

# -eof meta-
