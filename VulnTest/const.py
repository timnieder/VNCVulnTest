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
    ZRLE = 16

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
    SetScale = 8
    SetSW = 10
    TextChat = 11
    PalmVNCSetScaleFactor = 15
    xvp = 250
    SetDesktopSize = 251
    gii = 253

class S2CMessages(IntEnum):
    #rfc
    FramebufferUpdate = 0
    SetColorMapEntries = 1
    Bell = 2
    ServerCutText = 3
    # extensions
    ResizeFramebuffer = 4
    FileTransfer = 7
    PalmVNCResizeFramebuffer = 15
    ServerState = 173
    xvp = 250
    gii = 253

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
    xvp = -309
    gii = -305
    ServerIdentity = 0xFFFE0003
    PointerPos = 0xFFFFFF18
    ExtendedDesktopSize = -308
    ExtendedViewSize = -307