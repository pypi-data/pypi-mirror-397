import can
import typing
import cantools
import cantools.database
from cantools.database.can.database import Database
from cantools.database.can.message import Message
from loguru import logger
from .parser import DbcBase, MessageNotFound, SignalNotFound


class DbcParser(DbcBase):

    def __init__(self, dbc_file) -> None:
        self.db: Database = typing.cast(
            Database, cantools.database.load_file(dbc_file))
        self.messages = {}
        # cache messages
        for m in self.db.messages:
            self.messages[m.frame_id] = m

    def __del__(self):
        pass

    def has_message(self, id) -> bool:
        return id in self.messages

    def get_message_by_name(self, name) -> Message:
        return self.db.get_message_by_name(name)

    def get_message_by_id(self, id) -> Message:
        return self.db.get_message_by_frame_id(id)

    def to_dict(self, msg: can.Message):
        message = self.get_message_by_id(msg.arbitration_id)
        signal = message.decode(msg.data)
        name = message.name
        logger.debug("name: {}, signal: {} {}", name, signal, type(signal))

        # support cantools 37.2.0
        # str(cantools.database.can.signal.NamedSignalValue) -> str
        _signal = {}
        for k,v in signal.items():
            logger.debug("signal: {} {} {}", k, v, type(v))
            _signal[k] = str(v)

        return {
            "id": hex(msg.arbitration_id),
            "name": name,
            "data": msg.data.hex(),
            "signal": _signal,
            "timestamp": msg.timestamp,
        }

    def from_dict(self, msg: dict):
        try:
            message = self.get_message_by_name(msg["name"])
        except Exception as e:
            raise MessageNotFound(e)
        try:
            frame = message.encode(msg["signal"])
        except Exception as e:
            raise SignalNotFound(e)
        return can.Message(
            arbitration_id=message.frame_id,
            data=frame,
            dlc=message.length,
            is_extended_id=False,
            is_fd=False,
            bitrate_switch=False,
            error_state_indicator=False,
            timestamp=msg["timestamp"],
        )