# Client
Security: (ClientConnection.cpp:ClientConnection::Authenticate)
- Legacy_SecureVNCPlugin
- Legacy_MSLogon
- ClientInitExtraMsgSupport (+\_new)
- UltraVNC
- SecureVNCPluginAuth (+\_new)
- SCPrompt
- SessionSelect
- MSLogon2Auth
- VNC
- Auth

Encoding: (ClientConnection::ReadScreenUpdate)
- LastRect
- NewFBSize
- ExtViewSize
- ExtendedDesktopSize
- XCursor
- RichCursor
- PointerPos

- CoRRE
- Ultra
- Ultra2
- UltraZip
- Cache
- CacheZip
- QueueZstd
- QueueZip
- ZstdHex
- Zlib
- ZlibHex
- Tight
- TightZstd
- ZYWRLE
- ZSTDRLE
- ZSTDYWRLE
- XZ
- XZYW


S2C:
(vncviewer/ClientConnection.cpp:ClientConnection::run_undetached?)
- FileTransfer (7)
- TextChat (11)
- ResizeFrameBuffer (4)
- Palm VNC ReSizeFrameBuffer (0xF)
- ServerState (0xAD)
- keepalive (13)
- requestsession (20)
- NotifyPluginStreaming (80)

# Server
Security Types: (vncclient.cpp:vncClientThread::AuthenticateClient)
- UltraVNC
- ClientInitExtraMsgSupportNew
- UltraVNC_SecureVNCPlugin
- UltraVNC_SecureVNCPlugin_New
- UltraVNC_SCPrompt
- UltraVNC_SessionSelect
- MSLogon2Auth
- None
- VNC

Encodings: (winvnc/vncencodemgr.h:vncEncodeMgr::SetEncoding)
- CopyRect
- ZRLE
- XZ
- Tight
- Ultra
- Ultra2
- Zlib
- ZlibHex
- RRE
- CoRRE
- ZSTDRLE
- ZSTDYWRLE
- ZYWRLE
- XZYW
- Zstd
- ZstdHex
- TightZstd
- Hextile

Pseudo: (winvnc/winvnc/vncclient.cpp:vncClientThread::run.SetEncodings)
- NewFBSize
- ExtendedDesktopSize
- CacheEnable
- QueueEnable
- CompressLevel0-9
- QualityLevel0-9
- FineQualityLevel0-00
- EncodingSubsamp1X-16X
- LastRect
- XCursor
- RichCursor
- ServerState
- PointerPos
- PseudoSession
- EnableKeepAlive
- EnableIdleTime
- FTProcolVersion
- ExtendedClipboard
- PluginStreaming
- GII


C2S: (winvnc/winvnc/vncclient.cpp:vncClientThread::run)
- GII (253)
- ExtendedClientCutText
- palmVNC SetScaleFactor
- SetScale
- SetServerInput
- SetDesktopSize
- SetSW
- TextChat (11)
- FileTransfer (7)
- NotifyPluginStreaming (80)