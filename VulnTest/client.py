from asyncio import StreamReader, StreamWriter, open_connection, run, sleep
from dataclasses import field
from rfbDes import RFBDes # rfbDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
from helper import read_int, read_text
from pixelFormat import PixelFormat, pixelformat2bytes, read_pixelformat
from const import Encodings, C2SMessages

class Client:
    reader: StreamReader = field(repr=False)
    writer: StreamWriter = field(repr=False)

    # connect
    async def connect(self, host, port):
        self.reader, self.writer = await open_connection(host, port)

    async def disconnect(self):
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

    # protocol handshake
    async def intro(self, bytes=b'RFB 003.008\n'):
        intro = await self.reader.readline()
        if intro[:4] != b'RFB ':
            raise ValueError(f'not a VNC server: {intro}')
        self.writer.write(bytes)

    # security handshake
    async def security(self, password):
        # read auth types
        numberOfTypes = await read_int(self.reader, 1)
        auth_types = set(await self.reader.readexactly(numberOfTypes))
        print(f"auth_types: {auth_types}")

        # select auth type
        for auth_type in (1, 2):
            if auth_type in auth_types:
                self.writer.write(auth_type.to_bytes(1, 'big'))
                break

        print(f"selected auth_type: {auth_type}")
        return await self.authenticate(auth_type, password)

    async def authenticate(self, auth_type, password):
        # VNC auth
        if auth_type == 2:
            if password is None:
                raise ValueError('server requires password')
            pw = (password + '\0' * 8)[:8] # pad with zeros to 8 chars
            des = RFBDes(pw.encode("ASCII")) # using DES
            challenge = await self.reader.readexactly(16)
            response = des.encrypt(challenge)
            self.writer.write(response)

        auth_result = await read_int(self.reader, 4)
        if auth_result == 0:
            print("auth successful")
            return True
        elif auth_result == 1:
            print("auth failed")
            reason = await read_text(self.reader)
            print(f"reason: {reason}")
            return False
        else:
            print(f"auth_result: {auth_result}")
            return False

    async def clientInit(self):
        msg = bytes()
        shared_flag = int(1)
        msg += shared_flag.to_bytes(1, "big")
        self.writer.write(msg)

    async def setPixelFormat(self, pixelFormat: PixelFormat):
        msg = bytes()
        message_type = int(C2SMessages.SetPixelFormat)
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(3, "big")
        msg += pixelformat2bytes(pixelFormat)
        self.writer.write(msg)

    async def setEncodings(self, num: int, encodings: Collection[int]):
        msg = bytes()
        message_type = int(C2SMessages.SetEncodings)
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += num.to_bytes(2, "big")
        for encoding in encodings:
            msg += encoding.to_bytes(4, "big")
        self.writer.write(msg)

    async def framebufferUpdateRequest(self, incremental:bool, x:int, y:int, w:int, h:int):
        msg = bytes()
        message_type = int(C2SMessages.FramebufferUpdateRequest)
        msg += message_type.to_bytes(1, "big")
        msg += incremental.to_bytes(1, "big")
        msg += x.to_bytes(2, "big")
        msg += y.to_bytes(2, "big")
        msg += w.to_bytes(2, "big")
        msg += h.to_bytes(2, "big")
        self.writer.write(msg)
    
    async def keyEvent(self, down:bool, key:int):
        msg = bytes()
        message_type = int(C2SMessages.KeyEvent)
        msg += message_type.to_bytes(1, "big")
        msg += down.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(2, "big")
        msg += key.to_bytes(4, "big")
        self.writer.write(msg)
    
    async def pointerEvent(self, mask:int, x:int, y:int):
        msg = bytes()
        message_type = int(C2SMessages.PointerEvent)
        msg += message_type.to_bytes(1, "big")
        msg += mask.to_bytes(1, "big")
        msg += x.to_bytes(2, "big")
        msg += y.to_bytes(2, "big")
        self.writer.write(msg)

    async def clientCutText(self, length, text):
        msg = bytes()
        message_type = int(C2SMessages.ClientCutText)
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(3, "big")
        msg += length.to_bytes(4, "big")
        msg += text.encode("latin-1")
        self.writer.write(msg)

    # raw event that writes faulty packages
    async def rawEvent(self, message_type:int, data:Collection[Tuple[int,int]]):
        msg = bytes()
        msg += message_type.to_bytes(1, "big")
        for d in data:
            length = d[0]
            dat = d[1]
            msg += dat.to_bytes(length, "big")
        self.writer.write(msg)

    async def ServerInit(self):
        w = await read_int(self.reader, 2)
        h = await read_int(self.reader, 2)
        # server pixel format
        format = await read_pixelformat(self.reader)

        name = await read_text(self.reader)

        return w,h,format
    
    # s2c messages # skip reading message type as its probably read beforehand
    async def framebufferUpdate(self, pixelFormat): # 0
        await self.reader.readexactly(1) # padding
        num = await read_int(self.reader, 2)
        for i in range(num):
            x = await read_int(self.reader, 2) # x-position
            y = await read_int(self.reader, 2) # y-position
            w = await read_int(self.reader, 2) # width
            h = await read_int(self.reader, 2) # height
            encoding = await read_int(self.reader, 4) # encoding-type
            if encoding == Encodings.Raw:
                data = self.reader.readexactly(w*h*pixelFormat.bitsPerPixel)
            else:
                raise Exception(f"unknown encoding {encoding}")
        return

    async def setColorMapEntries(self) -> List[Tuple]: # 1
        colors = []
        await self.reader.readexactly(1) # padding
        first = await read_int(self.reader, 2) # first-color
        num = await read_int(self.reader, 2) # number-of-colors
        for i in range(num):
            r = await read_int(self.reader, 2) # red
            g = await read_int(self.reader, 2) # green
            b = await read_int(self.reader, 2) # blue
            colors.append((r,g,b))
        return colors

    async def bell(self):
        # no data
        return
    
    async def serverCutText(self) -> str: # 3
        await self.reader.readexactly(3) # padding
        text = await read_text(self.reader)
        return text

    async def fileTransfer(self):
        contentType = await read_int(self.reader, 1)
        contentParam = await read_int(self.reader, 1)
        await self.reader.readexactly(1) # padding
        size = await read_int(self.reader, 4)
        length = await read_int(self.reader, 4)
        data = await self.reader.readexactly(length)
        return contentType, contentParam, size, data

    async def sendFileTransfer(self, contentType:int, contentParam:int, size:int, length:int, data:bytes):
        msg = bytes()
        message_type = int(C2SMessages.FileTransfer)
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += contentType.to_bytes(1, "big")
        msg += contentParam.to_bytes(1, "big")
        msg += padding.to_bytes(1, "big")
        msg += size.to_bytes(4, "big")
        msg += length.to_bytes(4, "big")
        msg += data
        self.writer.write(msg)
