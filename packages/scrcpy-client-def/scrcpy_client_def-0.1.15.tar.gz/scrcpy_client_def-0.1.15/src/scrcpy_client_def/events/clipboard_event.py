import struct
from enum import IntEnum
from ..defs import ControlMsgType, DeviceMsgType

class CopyKey(IntEnum):
    COPY_KEY_NONE = 0
    COPY_KEY_COPY = 1
    COPY_KEY_CUT  = 2

class GetClipboardEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_GET_CLIPBOARD
    copy_key: CopyKey = CopyKey.COPY_KEY_COPY

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BB",
            self.msg_type.value,
            self.copy_key.value,
        )
        return buf

"""
This event is sent with the latest clipboard content from server to the client
when the clipboard of the Android side updated.
"""
class GetClipboardEventResponse:
    @staticmethod
    def consume(data: bytes) -> tuple[str, bytes] | None:
        msg_type = data[0]
        if msg_type != DeviceMsgType.DEVICE_MSG_TYPE_CLIPBOARD:
            return None
        if len(data) < 5:
            # at least type + empty string length
            return None
        clipboard_len: int = struct.unpack(">I", data[1:5])[0]
        if clipboard_len > len(data) - 5:
            return None
        try:
            parsed_text = data[5:5+clipboard_len].decode("utf-8")
            remain_data = data[5+clipboard_len:]
            return parsed_text, remain_data
        except UnicodeDecodeError:
            return None

class SetClipboardEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_SET_CLIPBOARD
    sequence: int = 0 # 8
    paste: int = 0 # 1

    def __init__(self, text: str) -> None:
        self.text = bytes(text, encoding="utf-8")

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BQBI",
            self.msg_type.value,
            self.sequence,
            self.paste,
            len(self.text),
        )
        buf += self.text
        return buf

"""
This event is sent from server to the client,
as a response to the request to set clipboard.
"""
class SetClipboardAckEvent:
    @staticmethod
    def consume(data: bytes) -> tuple[int, bytes] | None:
        msg_type = data[0]
        if msg_type != DeviceMsgType.DEVICE_MSG_TYPE_ACK_CLIPBOARD:
            return None
        if len(data) < 9:
            return None
        sequence: int = struct.unpack(">Q", data[1:9])[0]
        remain_data = data[9:]
        return sequence, remain_data
