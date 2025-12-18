import can


class SignalNotFound(Exception):
    pass


class MessageNotFound(Exception):
    pass


class DbcBase(object):

    def to_dict(self, msg: can.Message):
        raise NotImplementedError

    def from_dict(self, msg: dict) -> can.Message:
        raise NotImplementedError
    
    def has_message(self, id) -> bool:
        raise NotImplementedError
