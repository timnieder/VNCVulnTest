filter: `vnc && (vnc.client_message_type == 7 || vnc.server_message_type == 7)`
UltraVNC
## setup
Client: SetEncoding with Pseudo FTProtocolVersion (`0xFFFF8002`)
Server: sends ft version
```
0000   07 11 03 00 00 00 00 00 00 00 00 00               ............
```
=> Type: rfbFileTransferProtocolVersion (0x11/17), Param: rfbFileTransferVersion (3)

## test permission
Client: TestPermission
```
0000   07 07 03 00 00 00 00 00 00 00 00 00               ............
```
type: rfbAbortFileTransfer (7), param = 3
Server: 
```
0000   07 0e 00 00 00 00 00 01 00 00 00 00               ............
```
type: rfbFileTransferAccess (14), size = 1

## start
Client: SessionStart (gui opened)
```
0000   07 0f 00 00 00 00 00 00 00 00 00 00               ............
```

Client: list drives
```
0000   07 01 02 00 00 00 00 00 00 00 00 00               ............
```
Server: dir list
```
0000   07 02 03 00 00 00 00 00 00 00 00 04 43 3a 6c 00   ............C:l.
```

Client: list dir
```
0000   07 01 01 00 00 00 00 00 00 00 00 03 43 3a 5c      ............C:\
```
Server: long ass message with dir content

Client: list dir
```
0000   07 01 01 00 22 00 00 80 00 00 00 0a 43 3a 5c 78   ....".......C:\x
0010   61 6d 70 70 70 5c                                 amppp\
```
Server: dir content
```
0000   07 02 01 00 00 00 00 00 00 00 00 0a 43 3a 5c 78   ............C:\x
0010   61 6d 70 70 70 5c 07 02 01 00 00 00 00 00 00 00   amppp\..........
0020   00 30 10 00 00 00 6b 08 d9 47 6e 7a d4 01 9c d4   .0....k..Gnz....
0030   58 b7 89 73 d9 01 9c d4 58 b7 89 73 d9 01 00 00   X..s....X..s....
0040   00 00 00 00 00 00 00 00 00 00 72 00 72 00 2e 2e   ..........r.r...
0050   00 70 07 02 01 00 00 00 00 00 00 00 00 3a 20 00   .p...........: .
0060   00 00 a1 87 b4 b0 89 73 d9 01 b9 92 8e bd 89 73   .......s.......s
0070   d9 01 b9 92 8e bd 89 73 d9 01 00 00 00 00 04 00   .......s........
0080   00 00 00 00 00 00 72 00 72 00 64 6f 77 6e 6c 6f   ......r.r.downlo
0090   61 64 2e 74 78 74 00 61 07 02 01 00 00 00 00 00   ad.txt.a........
00a0   00 00 00 38 10 00 00 00 c0 3e ca 04 6f 7a d4 01   ...8.....>..oz..
00b0   2d 73 61 87 af 4f d6 01 2d 73 61 87 af 4f d6 01   -sa..O..-sa..O..
00c0   00 00 00 00 00 00 00 00 00 00 00 00 72 00 72 00   ............r.r.
00d0   70 68 70 4d 79 41 64 6d 69 6e 00 74 07 02 00 00   phpMyAdmin.t....
00e0   00 00 00 00 00 00 00 00                           ........
```

## download
Client: Request file
```
0000   07 03 00 00 00 00 00 00 00 00 00 16 43 3a 5c 78   ............C:\x
0010   61 6d 70 70 70 5c 64 6f 77 6e 6c 6f 61 64 2e 74   amppp\download.t
0020   78 74                                             xt
```
type: rfbFileTransferRequest (3)
Server: file header
```
0000   07 04 00 00 00 00 00 04 00 00 00 27 43 3a 5c 78   ...........'C:\x
0010   61 6d 70 70 70 5c 64 6f 77 6e 6c 6f 61 64 2e 74   amppp\download.t
0020   78 74 2c 30 34 2f 32 30 2f 32 30 32 33 20 31 33   xt,04/20/2023 13
0030   3a 31 32 00 00 00 00                              :12....
```
type: rfbFileHeader(3), size = 4, length = 39, data: dl file path + 4 bytes = 0

Client: ready to receive file
```
0000   07 04 01 70 00 00 00 04 00 00 00 00               ...p........
```
type: rfbFileHeader (4), size: 4 => ready cause size > 0
Server: content
```
0000   07 05 00 00 00 00 00 00 00 00 00 04 31 32 33 34   ............1234
```
type: rfbFilePacket (5), length: 4
Server: file done
```
0000   07 06 00 00 00 00 00 00 00 00 00 00               ............
```
type: rfbEndOfFile (6)

## upload
Client: FileTransferOffer
```
0000   07 08 00 00 00 00 00 03 00 00 00 25 43 3a 5c 78   ...........%C:\x
0010   61 6d 70 70 70 5c 75 70 6c 6f 61 64 2e 74 78 74   amppp\upload.txt
0020   2c 30 34 2f 32 30 2f 32 30 32 33 20 31 33 3a 31   ,04/20/2023 13:1
0030   30 00 00 00 00                                    0....
```
Server: accept
```
0000   07 09 00 00 00 00 00 00 00 00 00 1d 43 3a 5c 78   ............C:\x
0010   61 6d 70 70 70 5c 21 55 56 4e 43 50 46 54 2d 75   amppp\!UVNCPFT-u
0020   70 6c 6f 61 64 2e 74 78 74                        pload.txt
```
type: rfbFileAcceptHeader (9), length = 29, data = destname
Client: file content
```
0000   07 05 00 00 00 00 00 00 00 00 00 03 31 32 33      ............123
```
Client: transfer done
```
0000   07 06 67 14 fd 7f 00 00 00 00 8a ae               ..g.........
```
Client: get dir content
...

## end
Client: session end (gui closed)
```
0000   07 10 00 00 00 00 00 00 00 00 00 00               ............
```


# Download Exploit
Client connects
Authorization and such
Client sends encoding FTProtocolVersion
Server sends FileTransfer with type `FileTransferProtocolVersion` and param `3`
Server sends FileTransfer with type `FileTransferAccess` and size `1` (to authorize filetransfer on the client)
Server sends FileTransfer with type `FileHeader`, size `<payload_length>`, length `<data_length>` - 4, data: `<remote_path>,<timestamp>\x00000000`
=> client crashes during 
```
*strrchr(szDestPath, '\\') = '\0'; // We don't handle UNCs for now
```
in FileTransfer::ReceiveFile, because current destination path is empty (cause file window wasnt opened yet)
=> if path isn't empty, will download (and potentially OVERWRITE) files in the selected dir. if it's empty crashes


Try to set current path remotely?
Set in `FileTransfer::ResolvePossibleShortcutFolder` or `FileTransfer::PopulateLocalListBox`.
`ResolvePossibleShortcutFolder` is only called from `PopulateLocalListBox`
=> dont think there is a way to remotely do that


# Upload Exploit
Client connects
Authorization and such
Client sends encoding FTProtocolVersion
Server sends FileTransfer with type `FileTransferProtocolVersion` and param `3`
Server sends FileTransfer with type `FileAcceptHeader` and path
=> crashes cause local file path is empty
=> set file path remotely? => set in `FileTransfer::OfferLocalFile`

=> `m_iFile` is also set after pressing the "receive" button.
=> exploit works
User goes into local folder with n files
User selects n files on the server and clicks "receive", with n > 2
Client sends FileTransferRequest for the first file
Server sends FileAcceptHeader with an arbitrary path
(Internally the client fails to send the first message, so he offers the next one. As the filelists is a shared index list he will use the selected index of the remote files)
Client sends FileTransferOffer for the 2nd file
Server sends FileAcceptHeader with an arbitrary path
Client sends FilePacket with the content of the 2nd File
Proceeds till n


# Path Traversal
File name = `strcat_s(m_szDestFileName, make_temp_filename(strrchr(szRemoteFileName, '\\') + 1).c_str());
=> only checks for `\\`
Uses CreateFileA: https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilea
=> `The name of the file or device to be created or opened. You may use either forward slashes (/) or backslashes (\) in this name.`
https://learn.microsoft.com/en-us/windows/win32/fileio/naming-a-file#naming-conventions

Send path `C:\\1/download.txt,04/20/2023 13:12`
=> doesn't work cause it prepends a temp file name resulting in
`<selected-folder>/!UVNCPFT-1/download.txt`
=> fails because folder `!UVNCPFT-1` doesn't exist
=>
Send path `C:\\/../1/download.txt,04/20/2023 13:12`
=> results in `<selected-folder>/!UVNCPFT-/../1/download.txt`
=> resolves to `<selected-folder>/1/download.txt`
=> works