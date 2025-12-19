from enum import IntEnum

class DeviceMsgType(IntEnum):
    DEVICE_MSG_TYPE_CLIPBOARD = 0
    DEVICE_MSG_TYPE_ACK_CLIPBOARD = 1
    DEVICE_MSG_TYPE_UHID_OUTPUT = 2
