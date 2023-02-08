from asyncio import StreamReader, StreamWriter, open_connection, run, sleep, start_server
from dataclasses import field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # pip install cryptography
from rfbDes import RFBDes # rfbDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
from tabulate import tabulate
import secrets

async def read_int(reader: StreamReader, length: int) -> int:
    """
    Reads, unpacks, and returns an integer of *length* bytes.
    """

    return int.from_bytes(await reader.readexactly(length), 'big')

async def text2bytes(length: int, text: str, encoding: str = "latin-1") -> bytes:
    """
    Encodes the string and length into bytes
    """
    msg = bytes()
    # length
    msg += length.to_bytes(4, "big")
    # data
    msg += text.encode(encoding)
    return msg

class Server:
    reader: StreamReader = field(repr=False)
    writer: StreamWriter = field(repr=False)

    async def listen(self, callback, host = "127.0.0.1", port = 5900):
        server = await start_server(callback, host, port)
        print(f"serving on {host}:{port}")
        async with server:
            await server.serve_forever()

    async def intro(self):
        self.writer.write(b'RFB 003.008\n')
        intro = await self.reader.readline()
        if intro[:4] != b'RFB ':
            raise ValueError(f'not a VNC client: {intro}')

    async def security(self, num, encodings: Collection[int]) -> int:
        msg = bytes()
        msg += num.to_bytes(1, "big")
        for encoding in encodings:
            msg += encoding.to_bytes(1, "big")
        self.writer.write(msg)
        return await read_int(self.reader, 1)
    
    async def failedSecurity(self, num, encodings: Collection[int], reasonLength, reason):
        msg = bytes()
        msg += num.to_bytes(1, "big")
        for encoding in encodings:
            msg += encoding.to_bytes(1, "big")
        self.writer.write(msg)
        r = await text2bytes(reasonLength, reason)
        self.writer.write(r)

    async def vncAuth(self, password: str) -> bool:
        pw = (password + '\0' * 8)[:8] # pad with zeros to 8 chars
        des = RFBDes(pw.encode("ASCII")) # using DES
        # generate challenge
        challenge = secrets.token_bytes(16)
        # generate response
        response = des.encrypt(challenge)
        # send the challenge
        self.writer.write(challenge)
        # check if response == encrypted challenge
        clientRes = await self.reader.readexactly(16)
        return response == clientRes

    async def securityResult(self, result):
        self.writer.write(result.to_bytes(4, "big"))

    async def securityResultReason(self, reasonLength, reason):
        r = await text2bytes(reasonLength, reason)
        self.writer.write(r)

    async def clientInit(self) -> int:
        return await read_int(self.reader, 1)

    async def serverInit(self, w, h, nameLength, name):
        msg = bytes()
        msg += w.to_bytes(2, "big")
        msg += h.to_bytes(2, "big")
        # pixelformat
        msg += int(32).to_bytes(1, "big") # bits per pixel
        msg += int(32).to_bytes(1, "big") # depth
        msg += bool(False).to_bytes(1, "big") # big endian
        msg += bool(True).to_bytes(1, "big") # true color
        msg += int(255).to_bytes(2, "big") # red max
        msg += int(255).to_bytes(2, "big") # green max
        msg += int(255).to_bytes(2, "big") # blue max
        msg += int(16).to_bytes(1, "big") # red shift
        msg += int(8).to_bytes(1, "big") # green shift
        msg += int(0).to_bytes(1, "big") # blue shift
        # padding
        msg += int(0).to_bytes(3, "big")
        # length
        msg += await text2bytes(nameLength, name)
        self.writer.write(msg)

    # c2s messages
    async def framebufferUpdateRequest(self):
        # skip reading message type as its probably read beforehand
        incremental = await read_int(self.reader, 1)
        x = await read_int(self.reader, 2)
        y = await read_int(self.reader, 2)
        w = await read_int(self.reader, 2)
        h = await read_int(self.reader, 2)

    # s2c messages
    async def framebufferUpdate(self, num, rectangles:Collection[int], pixelData:Collection[bytes]):
        msg = bytes()
        message_type = 0
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += num.to_bytes(2, "big")
        for i in range(len(rectangles)):
            # rectangle
            rectangle = rectangles[i]
            msg += rectangle[0].to_bytes(2, "big") # x
            msg += rectangle[1].to_bytes(2, "big") # y
            msg += rectangle[2].to_bytes(2, "big") # w
            msg += rectangle[3].to_bytes(2, "big") # h
            msg += rectangle[4].to_bytes(4, "big") # encoding-type
            # pixel data
            data = pixelData[i]
            msg += data
        self.writer.write(msg)

    async def setColorMapEntries(self, colorIndex: int, num: int, colors: Collection[Collection[int]]):
        msg = bytes()
        message_type = 1
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += colorIndex.to_bytes(2, "big") # first-color
        msg += num.to_bytes(2, "big") # number-of-colors
        for color in colors:
            msg += color[0].to_bytes(2, "big") # red
            msg += color[1].to_bytes(2, "big") # green
            msg += color[2].to_bytes(2, "big") # blue
        self.writer.write(msg)

    async def serverCutText(self, length: int, text: str):
        msg = bytes()
        message_type = 1
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += await text2bytes(length, text)
        self.writer.write(msg)

async def main():
    server = Server()
    w = 800
    h = 600
    async def callback(reader, writer):
        server.reader = reader
        server.writer = writer
        await server.intro()
        auth_type = await server.security(1, [2])
        authed = True
        if auth_type == 2:
            authed = await server.vncAuth("1234")
        result = 1
        if authed == True:
            result = 0
        await server.securityResult(result)
        if authed == False:
            reason = "wrong password!"
            await server.securityResultReason(len(reason), reason)
        sharedFlag = await server.clientInit()
        await server.serverInit(w, h, 7, "Desktop")
        
        # TODO: parse client messages
        
        print("server done")
    
    host = "127.0.0.1"
    port = 5900
    await server.listen(callback, host, port)

# TODO: tests
run(main())