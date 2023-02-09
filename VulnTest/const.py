from enum import IntEnum

class SecurityTypes(IntEnum):
    INVALID = 0
    NONE = 1
    VNC = 2

class SecurityResult(IntEnum):
    OK = 0
    FAILED = 1 