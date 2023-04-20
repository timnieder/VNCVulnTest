from enum import IntEnum

class SecurityTypes(IntEnum):
    INVALID = 0
    NONE = 1
    VNC = 2

class SecurityResult(IntEnum):
    OK = 0
    FAILED = 1 

class Encodings(IntEnum):
    Raw = 0
    RRE = 2

class C2SMessages(IntEnum):
    #rfc
    SetPixelFormat = 0
    SetEncodings = 2
    FramebufferUpdateRequest = 3
    KeyEvent = 4
    PointerEvent = 5
    ClientCutText = 6
    # extensions
    FileTransfer = 7

class S2CMessages(IntEnum):
    #rfc
    FramebufferUpdate = 0
    SetColorMapEntries = 1
    Bell = 2
    ServerCutText = 3
    # extensions
    FileTransfer = 7

class FileTransferMessages(IntEnum):
    DirContentRequest = 1
    DirPacket = 2
    FileTransferRequest = 3
    FileHeader = 4
    FilePacket = 5
    EndOfFile = 6
    AbortFileTransfer = 7
    FileTransferOffer = 8
    FileAcceptHeader = 9
    Command = 10
    CommandReturn = 11
    FileChecksums = 12
    FileTransferAccess = 14
    FileTransferSessionStart = 15
    FileTransferSessionEnd = 16
    FileTransferProtocolVersion = 17

class PseudoEncodings(IntEnum):
    FTProcolVersion = -32766