from asyncio import StreamReader, StreamWriter, open_connection, run, sleep
from dataclasses import field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # pip install cryptography
from rfbDes import RFBDes # rfbDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
from helper import read_int, read_text

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
        shared_flag = int(1)
        self.writer.write(shared_flag.to_bytes(1, "big"))

    async def setEncodings(self, num: int, encodings: Collection[int]):
        message_type = int(2)
        self.writer.write(message_type.to_bytes(1, "big"))
        padding = int(0)
        self.writer.write(padding.to_bytes(1, "big"))
        self.writer.write(num.to_bytes(2, "big"))
        for encoding in encodings:
            self.writer.write(encoding.to_bytes(4, "big"))

    async def framebufferUpdateRequest(self, incremental:bool, x:int, y:int, w:int, h:int):
        message_type = int(3)
        self.writer.write(message_type.to_bytes(1, "big"))
        self.writer.write(incremental.to_bytes(1, "big"))
        self.writer.write(x.to_bytes(2, "big"))
        self.writer.write(y.to_bytes(2, "big"))
        self.writer.write(w.to_bytes(2, "big"))
        self.writer.write(h.to_bytes(2, "big"))
    
    async def keyEvent(self, down:bool, key:int):
        message_type = int(4)
        self.writer.write(message_type.to_bytes(1, "big"))
        self.writer.write(down.to_bytes(1, "big"))
        padding = int(0)
        self.writer.write(padding.to_bytes(2, "big"))
        self.writer.write(key.to_bytes(4, "big"))
    
    async def pointerEvent(self, mask:int, x:int, y:int):
        message_type = int(5)
        self.writer.write(message_type.to_bytes(1, "big"))
        self.writer.write(mask.to_bytes(1, "big"))
        self.writer.write(x.to_bytes(2, "big"))
        self.writer.write(y.to_bytes(2, "big"))

    async def clientCutText(self, length, text):
        message_type = int(6)
        self.writer.write(message_type.to_bytes(1, "big"))
        padding = int(0)
        self.writer.write(padding.to_bytes(3, "big"))
        self.writer.write(length.to_bytes(4, "big"))
        self.writer.write(text.encode("latin-1"))

    # raw event that writes faulty packages
    async def rawEvent(self, message_type:int, data:Collection[Tuple[int,int]]):
        self.writer.write(message_type.to_bytes(1, "big"))
        for d in data:
            length = d[0]
            dat = d[1]
            self.writer.write(dat.to_bytes(length, "big"))

    async def ServerInit(self):
        w = await read_int(self.reader, 2)
        h = await read_int(self.reader, 2)
        # server pixel format
        bpp = await read_int(self.reader, 1)
        depth = await read_int(self.reader, 1)
        bigEndian = await read_int(self.reader, 1)
        trueColor = await read_int(self.reader, 1)
        redMax = await read_int(self.reader, 2)
        greenMax = await read_int(self.reader, 1)
        blueMax = await read_int(self.reader, 2)
        redShift = await read_int(self.reader, 1)
        greenShift = await read_int(self.reader, 1)
        blueShift = await read_int(self.reader, 1)
        padding = await self.reader.readexactly(3)

        name = await read_text(self.reader)

        return w,h