import can
from canlib import kvadblib
from canlib.frame import Frame
from canlib.kvadblib import FrameBox
from canlib.kvadblib import Message
from canlib.kvadblib.bound_signal import BoundSignal
from canlib.kvadblib.bound_message import BoundMessage
from .parser import DbcBase, MessageNotFound, SignalNotFound
from loguru import logger


class DbcParser(DbcBase):

    def __init__(self, dbc_file) -> None:
        self.db = kvadblib.Dbc(dbc_file)
        self.fb = FrameBox(self.db, self.db.messages())
        self.messages = {}
        # cache messages
        for m in self.db.messages():
            self.messages[m.id] = m
            logger.debug("message: {} - {}", m.id, m.name)

    def __del__(self):
        self.db.close()

    def has_message(self, id) -> bool:
        return id in self.messages

    def get_message_by_name(self, name) -> Message:
        return self.db.get_message_by_name(name)

    def get_message_by_id(self, id) -> Message:
        return self.db.get_message_by_id(id, 0)

    def to_dict(self, msg: can.Message):
        frame = Frame(msg.arbitration_id, msg.data, dlc=msg.dlc)
        message = self.get_message_by_id(msg.arbitration_id)
        bound_msg = BoundMessage(message, frame)
        signal = {signal.name: signal.value for signal in bound_msg}
        name = message.name

        return {
            "id": hex(msg.arbitration_id),
            "name": name,
            "data": msg.data.hex(),
            "signal": signal,
            "timestamp": msg.timestamp,
        }

    def from_dict(self, msg: dict):
        signal = msg["signal"]
        try:
            for signal_name, signal_value in signal.items():
                bs: BoundSignal = self.fb.signal(signal_name)
                if bs.is_enum:
                    bs.raw = bs.signal.enums[signal_value]
                else:
                    bs.phys = signal_value
        except Exception as e:
            raise SignalNotFound(e)
        try:
            message: BoundMessage = self.fb.message(msg["name"])
        except Exception as e:
            raise MessageNotFound(e)

        frame: Frame = message._frame
        return can.Message(
            arbitration_id=frame.id,
            data=frame.data,
            dlc=frame.dlc,
            is_extended_id=False,
            is_fd=False,
            bitrate_switch=False,
            error_state_indicator=False,
            timestamp=msg["timestamp"],
        )
