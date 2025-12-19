import struct
from dataclasses import dataclass
from ..defs import ControlMsgType, DeviceMsgType, SDL_Scancode,\
                   HID_ID_KEYBOARD, HID_ID_MOUSE, HID_KEYBOARD_INPUT_SIZE, HID_KEYBOARD_MAX_KEYS, HID_KEYBOARD_REPORT_DESC, HID_MOUSE_INPUT_SIZE, HID_MOUSE_REPORT_DESC, KeymodStateStore, MouseButtonStateStore
from ..utils import clamp

"""
This event is sent from server to client, indicates the HID keyboard outputs.
"""
class HIDOutputEvent:
    @dataclass
    class HIDOutput:
        id: int   # 16
        size: int # 16
        data: bytes

    @staticmethod
    def consume(data: bytes) -> tuple[HIDOutput, bytes] | None:
        msg_type = data[0]
        if msg_type != DeviceMsgType.DEVICE_MSG_TYPE_UHID_OUTPUT:
            return None
        if len(data) < 5:
            # length of msg_type + id + size is 5
            return None
        id_, size = struct.unpack(">HH", data[1:5])
        if size > len(data) - 5:
            # did not received all data
            return None
        return HIDOutputEvent.HIDOutput(id_, size, data[5:5+size]), data[5+size:]

class HIDKeyboardInitEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_CREATE # 8
    id_ = HID_ID_KEYBOARD # 16
    vendor_id = 0 # 16
    product_id = 0 # 16
    name = "" # 8
    report_desc_size: int = len(HID_KEYBOARD_REPORT_DESC) # 16
    report_desc: bytes = HID_KEYBOARD_REPORT_DESC
    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHHH",
            self.msg_type.value,
            self.id_,
            self.vendor_id,
            self.product_id,
        )
        name_bytes = self.name.encode('utf-8')[:127]
        buf += struct.pack('B', len(name_bytes)) + name_bytes
        buf += struct.pack('>H', len(self.report_desc))
        buf += self.report_desc
        return buf

class HIDKeyboardInputEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_INPUT # 8
    id_: int = HID_ID_KEYBOARD # 16
    size: int = HID_KEYBOARD_INPUT_SIZE # 16

    def __init__(self, data: list[int]) -> None:
        self.data = bytes(data)
    
    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHH",
            self.msg_type.value,
            self.id_,
            self.size,
        )
        buf += self.data
        return buf

def KeyEvent(keymod: KeymodStateStore, keys: list[SDL_Scancode]) -> HIDKeyboardInputEvent:
    # [_, _, _, _, _, _, _, _]
    # length: 8
    # 0 -> mod key
    # 1 -> reserved, always 0
    # 2 - 7 -> keys pressed the same time (scancode)
    data: list[int] = [0] * HIDKeyboardInputEvent.size
    data[0] = keymod.key

    data_ptr = 2
    for k in keys[:HID_KEYBOARD_MAX_KEYS]:
        data[data_ptr] = k.value
        data_ptr += 1
    keyboard_event = HIDKeyboardInputEvent(data)
    return keyboard_event

def KeyEmptyEvent() -> HIDKeyboardInputEvent:
    data = [0] * HIDKeyboardInputEvent.size
    keyboard_event = HIDKeyboardInputEvent(data)
    return keyboard_event

# --- --- --- --- --- ---

class HIDMouseInitEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_CREATE # 8
    id_ = HID_ID_MOUSE # 16
    vendor_id: int = 0 # 16
    product_id: int = 0 # 16
    name = "" # 8
    report_desc_size: int = len(HID_MOUSE_REPORT_DESC) # 16
    report_desc: bytes = HID_MOUSE_REPORT_DESC
    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHHH",
            self.msg_type.value,
            self.id_,
            self.vendor_id,
            self.product_id,
        )
        name_bytes = self.name.encode('utf-8')[:127]
        buf += struct.pack('B', len(name_bytes)) + name_bytes
        buf += struct.pack('>H', len(self.report_desc))
        buf += self.report_desc
        return buf

class HIDMouseInputEvent:
    msg_type: ControlMsgType = ControlMsgType.MSG_TYPE_UHID_INPUT # 8
    id_: int = HID_ID_MOUSE # 16
    size: int = HID_MOUSE_INPUT_SIZE # 16

    def __init__(self, data: list[int]) -> None:
        self.data = bytes(data)

    def serialize(self) -> bytes:
        buf = struct.pack(
            ">BHH",
            self.msg_type.value,
            self.id_,
            self.size,
        )
        buf += self.data
        return buf

def MouseMoveEvent(x: int, y: int, buttons_state: MouseButtonStateStore) -> HIDMouseInputEvent:
    data = [0, 0, 0, 0, 0]
    data[0] = buttons_state.mouse_button
    # When convert int into bytes, the int value can not be negative.
    # In the server side, the value over 127 will overflow, and will be converted into the correct negative value
    data[1] = clamp(x, -127, 127) % 256
    data[2] = clamp(y, -127, 127) % 256
    data[3] = 0
    data[4] = 0
    input_event = HIDMouseInputEvent(data)
    return input_event

def MouseClickEvent(buttons_state: MouseButtonStateStore) -> HIDMouseInputEvent:
    data = [0, 0, 0, 0, 0]
    data[0] = buttons_state.mouse_button
    input_event = HIDMouseInputEvent(data)
    return input_event

def MouseScrollEvent(dy: int, dx: int) -> HIDMouseInputEvent:
    data = [0, 0, 0, 0, 0]
    data[3] = clamp(dy, -127, 127) % 256
    data[4] = clamp(dx, -127, 127) % 256
    input_event = HIDMouseInputEvent(data)
    return input_event

def MouseEmptyEvent() -> HIDMouseInputEvent:
    data = [0, 0, 0, 0, 0]
    input_event = HIDMouseInputEvent(data)
    return input_event
