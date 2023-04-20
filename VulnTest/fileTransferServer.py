from server import Server, generateRREData
from const import SecurityTypes, SecurityResult, C2SMessages, Encodings, PseudoEncodings, FileTransferMessages
import datetime
from helper import read_int
from asyncio import run, CancelledError
from pixelFormat import PixelFormat

async def ftServer(server: Server):
    valid = await server.intro(b"RFB 003.008\n")
    if valid == False:
        raise Exception("not a rfb client")
    auth_type = await server.security(1, [SecurityTypes.NONE])
    #await server.vncAuth("12345678")
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")
    
    lastFramebufferTime = datetime.datetime.min
    framebufferCooldown = datetime.timedelta(seconds=5)
    # parse client messages
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            pixelFormat = await server.setPixelFormat()
            server.pixelFormat = pixelFormat
            print(f"SetPixelFormat: {pixelFormat}")
        elif message_type == C2SMessages.SetEncodings:
            encodings = await server.setEncodings()
            print(f"Encodings: {encodings}")
            if PseudoEncodings.FTProcolVersion in encodings:
                print("ft")
                await server.sendFileTransfer(FileTransferMessages.FileTransferProtocolVersion, 3, 0, 0, bytes())
        elif message_type == C2SMessages.FramebufferUpdateRequest:
            incremental, x, y, w, h = await server.framebufferUpdateRequest()
            now = datetime.datetime.now()
            delta = now - lastFramebufferTime
            if delta > framebufferCooldown:
                await server.framebufferUpdate(1, [(x,y,w,h, Encodings.RRE)], [(await generateRREData(w,h,server.pixelFormat))])
                lastFramebufferTime = now
                print("FramebufferUpdate")
        elif message_type == C2SMessages.KeyEvent:
            down, key = await server.keyEvent()
            print("KeyEvent")
        elif message_type == C2SMessages.PointerEvent:
            mask, x, y = await server.pointerEvent()
            #print("PointerEvent")
        elif message_type == C2SMessages.ClientCutText:
            text = await server.clientCutText()
            print("ClientCutText")
        elif message_type == C2SMessages.FileTransfer:
            type, param, size, data = await server.fileTransfer()
            print(f"filetransfer {type}")
            if type == FileTransferMessages.AbortFileTransfer:
                print("autorize")
                # authorize
                await server.sendFileTransfer(FileTransferMessages.FileTransferAccess, 0, 1, 0, bytes())
                path = "C:\\upload.txt"
                await server.sendFileTransfer(FileTransferMessages.FileAcceptHeader, 0, 0, len(path), path.encode("latin-1"))
            elif type == FileTransferMessages.FileHeader:
                print(f"fileheader: {size}")
                if size > 0:
                    content = "1234"
                    await server.sendFileTransfer(FileTransferMessages.FilePacket, 0, 0, len(content), content.encode("latin-1"))
                    #eof
                    await server.sendFileTransfer(FileTransferMessages.EndOfFile, 0, 0, 0, bytes())
            elif type == FileTransferMessages.DirContentRequest:
                if param == 2: # RDrivesList
                    print("RDrivesList")
                    drives = b"C:l\x00"
                    await server.sendFileTransfer(FileTransferMessages.DirPacket, 3, 0, 4, drives)
                if param == 1: # listdir
                    if data.decode("latin-1") != "C:\\":
                        print("force sending file")
                        # force dl
                        path = "C:\\download.txt,04/20/2023 13:12"
                        # length: path, size 4
                        await server.sendFileTransfer(FileTransferMessages.FileHeader, 0, 4, len(path), path.encode("latin-1"))
                        server.writer.write(int(0).to_bytes(4, "big")) # append size
                    else:
                        msg = bytes()
                        msg += b"\x43\x3a\x5c\x07\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x30\x10\x00\x00\x00\x6b\x08\xd9\x47\x6e\x7a\xd4\x01\x9c\xd4"
                        msg += b"\x58\xb7\x89\x73\xd9\x01\x9c\xd4\x58\xb7\x89\x73\xd9\x01\x00\x00"
                        msg += b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x72\x00\x72\x00\x2e\x2e"
                        msg += b"\x00\x70\x07\x02\x01\x00\x00\x00\x00\x00\x00\x00\x00\x3a\x20\x00"
                        msg += b"\x00\x00\xa1\x87\xb4\xb0\x89\x73\xd9\x01\xb9\x92\x8e\xbd\x89\x73"
                        msg += b"\xd9\x01\xb9\x92\x8e\xbd\x89\x73\xd9\x01\x00\x00\x00\x00\x04\x00"
                        msg += b"\x00\x00\x00\x00\x00\x00\x72\x00\x72\x00\x64\x6f\x77\x6e\x6c\x6f"
                        msg += b"\x61\x64\x2e\x74\x78\x74\x00\x61\x07\x02\x01\x00\x00\x00\x00\x00"
                        msg += b"\x00\x00\x00\x38\x10\x00\x00\x00\xc0\x3e\xca\x04\x6f\x7a\xd4\x01"
                        msg += b"\x2d\x73\x61\x87\xaf\x4f\xd6\x01\x2d\x73\x61\x87\xaf\x4f\xd6\x01"
                        msg += b"\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x72\x00\x72\x00"
                        msg += b"\x70\x68\x70\x4d\x79\x41\x64\x6d\x69\x6e\x00\x74\x07\x02\x00\x00"
                        msg += b"\x00\x00\x00\x00\x00\x00\x00\x00"
                        await server.sendFileTransfer(FileTransferMessages.DirPacket, 1, 0, 3, msg)
            elif type == FileTransferMessages.FileTransferRequest:
                print(f"wants {data.decode('latin-1')}. sending fake file")
                # force dl
                path = "C:\\download.txt,04/20/2023 13:12"
                # length: path, size 4
                await server.sendFileTransfer(FileTransferMessages.FileHeader, 0, 4, len(path), path.encode("latin-1"))
                server.writer.write(int(0).to_bytes(4, "big")) # append size
        else:
            print(f"unknown message type {message_type}")
    
    print("server done")

async def main(w,h):
    width = w
    height = h
    format = PixelFormat(32, 24, False, True, 255, 255, 255, 16, 8, 0)
    server = Server(width, height, format)
    host = "127.0.0.1"
    port = 5900
    async def callback(reader, writer):
        server.reader = reader
        server.writer = writer
        try:
            await ftServer(server)
        except Exception as e:
            print(f"Exception: {e}")
        await server.disconnect()
        server.server.close()
        await server.server.wait_closed()
    while True:
        try:
            await server.listen(callback, host, port)
        except CancelledError:
            print("Cancelled")
        except Exception as e:
            print(f"Exception: {e}")

run(main(1600,1200))