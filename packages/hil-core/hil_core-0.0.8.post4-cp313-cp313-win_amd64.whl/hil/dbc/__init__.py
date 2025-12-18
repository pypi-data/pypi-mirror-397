
try:
    from ._canlib import DbcParser as DbcParser
except ImportError:
    try:
        from ._cantools import DbcParser as DbcParser
    except ImportError:
        raise ImportError(
            "No DBC parser found. Please install canlib or cantools.")

from .parser import MessageNotFound, SignalNotFound
from loguru import logger

logger.disable("hil.dbc")
