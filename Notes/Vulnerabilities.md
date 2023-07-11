Scenarios:
- Malicious Client, Victim Server
- Victim Client, Malicious Server
- Malicious 3rd party, Victim Client and/or Server

Attacks:
- Out-of-State/order packets
- invalid packets
- Over/underflows in Packets:
		**Client**:
	- overlong intro
	- SetEncodings
	- FramebufferUpdateRequest x,y,w,h values
	- KeyEvent key?
	- PointerEvent x,y
	- ClientCutText
		**Server**:
	- overlong intro
	- Security Type during handshake
	- Reason during Security Handshake
	- Challenge during vnc auth
	- Reason during SecurityResult
	- ServerInit name
	- FramebufferUpdate number-of-rectangles + x,y,w,h values + pixeldata
	- SetColorMapEntries number-of-colors + color index
	- ServerCutText
		- TODO: pseudo encodings?
- Disconnect by ip spoof
- Many client connects
- auth bypass?

- [x] Find client/server lib that we can easily edit
- [x] Write tests
- [ ] Run on different clients and server


TODO:
- ubuntu server crashes sometimes when python program fails


# Extensions
Ideas:
- FileTransfer on view only system (ultravnc checks, tightvnc (other ft, only tight) checks too)
- Filetransfer: 
	- force client to download/accept file => **yes** (ultravnc: rfbFileHeader)
	- force client to upload file => **yes** (a bit convoluted but works)
	- use path as name to overwrite arbitrary files on the client => **yes** :(
	- change the name of the downloaded file (client wants evil.exe, we sent file with name good.exe) => **yes**
- gii on view only (ultravnc) => **yes**
- ServerIdentity Pseudo Int overflow (https://github.com/LibVNC/libvncserver/blob/0ff438b0bbe61df0aa139e48bc4f753de3eb197e/src/libvncclient/rfbclient.c#L2165, w=U16.max) => no
- PointerPos x,y values => no
- ExtendedDesktopSize number, screen x,y,w,h => no
- Extended ViewSize x,y,w,h => no
- ExtendedClient/ServerCutText caps sizes, request on viewonly, size
- ServerCutText request on viewonly/if clipboard disabled => **yes** (only ultra)
- FileTransfer
	- RDirContent:
		- ADrivesList long/overlong string
- SetScale scale == 0 => no
- SetScaleFactor scale == 0 => no
- SetSW x,y values => no
- textchat overlong/underlong text/length, open/close/finish twice => no
- EnableContinuousUpdates x,y,w,h values
- SetDesktopSize w,h,number-of-screens, screen x,y,w,h => no
- GII
	- Device creation: nums, valuator si_div == 0 => not evaluated
	- device destruction: device-origin => not implemented
	- event injection: idk
	- device creation response: just send a device-origin => 
- ServerState keepaliveinterval, idleinputtimeout => no
- ReSizeFrameBuffer w,h,d-w,d-h => see above