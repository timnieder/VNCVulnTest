# Client
Security (src/libvncclient/rfbclient.c:InitialiseRFBConnection)
- None
- VNC
- SASL
- UltraMSLogon2
- MSLogon
- Apple ARD
- TLS (None, vnc, sasl) (18)
- VeNCrypt (none, vnc, plain, sasl) (19)

Encodings: (HandleRFBServerMessage)
- Raw
- CopyRect
- RRE
- CoRRE (4)
- Hextile
- Zlib (6)
- Tight (7)
- Ultra (9)
- TRLE
- ZRLE
- ZYWRLE (17)
- UltraZip (10)

Pseudo:
- XCursor
- RichCursor
- PointerPos
- KeyboardLedState
- NewFBSize
- ExtendedDesktopSize
- SupportedMessages
- SupportedEncodings
- ServerIdentity
- QemuExtendedKeyEvent

S2C:  (HandleRFBServerMessage)
- ExtendedServerCutText (3) https://github.com/LibVNC/libvncserver/blob/master/src/libvncclient/rfbclient.c#L2516-L2564
- TextChat (11) https://github.com/LibVNC/libvncserver/blob/master/src/libvncclient/rfbclient.c#L2566-L2607
- xvp (250) https://github.com/LibVNC/libvncserver/blob/master/src/libvncclient/rfbclient.c#L2609-L2625
- ResizeFramebuffer (4) https://github.com/LibVNC/libvncserver/blob/master/src/libvncclient/rfbclient.c#L2627-L2643
- PalmVNCReSizeFramebuffer (15) https://github.com/LibVNC/libvncserver/blob/master/src/libvncclient/rfbclient.c#L2645-L2660

# Server
Security Types: (src/libvncserver/auth.c:rfbAuthNewClient)
- None
- VNC Auth

Encodings:
- Raw
- CopyRect
- RRE
- CoRRE
- Hextile
- Zlib
- Tight
- Zlibhex
- Ultra
- ZRLE
- ZYWRLE
- TightPNG

Pseudo: (rfbProcessClientNormalMessage.setencodings)
- NewFBSize
- LastRect
- PointerPos
- Rich cursor
- KeyboardLedState
- SupportedMessages
- SupportedEncodings
- ServerIdentity
- xvp
- extendedclipboard
- xcursor

C2S: https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2208 (rfbProcessClientNormalMessage)
- rfbFixColourMapEntries (1, unsupported) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2265-L2277
- filetransfer (7) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2707-L2719
- SetSW (SetSingleWindow) (10) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2721-L2737
- SetServerInput (9) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2739-L2755
- TextChat (11) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2757-L2813
- Extended ClientCutText (6) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2816-L2937
- PalmVNC SetScaleFactor (15) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2939-L2960
- SetScale (8) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2962-L2983
- xvp (250) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L2985-L3005
- SetDesktopSize (251) https://github.com/LibVNC/libvncserver/blob/master/src/libvncserver/rfbserver.c#L3007-L3073