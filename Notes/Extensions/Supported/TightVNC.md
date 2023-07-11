## Client
Security: (RemoveViewerCore::negotiateSecurityType)
- None
- VNC
- Tight (default tunnel, none, vnc, external? auth)

Encodings: (viewer-core::RemoveViewerCore.cpp:RemoteViewerCore::init)
- Raw
- CopyRect
- RRE
- Hextile
- Tight
- ZRLE
Pseudo:
- DesktopSize
- LastRect
- PointerPos
- RichCursor
- ExtendedDesktopSize

S2C: (viewer-core::RemoveViewerCore.cpp:RemoteViewerCore::execute)
- ServerCutText UTF8 (0xFC000200)

## Server
Security:
- None
- VNC
- TIGHT (no tunnel, none, vnc)

Encodings: (UpdateSender.cpp:UpdateSender)
- CopyRECT
- HEXTILE
- TIGHT
Pseudo:
- COMPR_LEVEL_0
- QUALITY_LEVEL_0
- RICH_CURSOR
- POINTER_POS

C2S: (rfb-sconn::RfbClient.cpp:RfbClient::execute, onRequest is called in RfbDispatcher.cpp)
- ECHO_REQUEST (0xFC000300)
- SetDesktopSize
- CLIENT_CUT_TEXT_UTF8 (0xFC000200)
- ENABLE_CUT_TEXT_UTF8 (0xFC000201)
- FileTransfer (FileTransferRequestHandler::onRequest, many messages, only tight?)
- RFB_VIDEO_FREEZE (152)