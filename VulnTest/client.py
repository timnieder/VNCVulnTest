from asyncio import StreamReader, StreamWriter, open_connection, run, sleep
from dataclasses import field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # pip install cryptography
import pyDes # pyDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
import time

host = "192.168.182.5"
port = 5900

async def read_int(reader: StreamReader, length: int) -> int:
    """
    Reads, unpacks, and returns an integer of *length* bytes.
    """

    return int.from_bytes(await reader.readexactly(length), 'big')

async def read_text(reader: StreamReader, encoding: str) -> str:
    """
    Reads, unpacks, and returns length-prefixed text.
    """

    length = await read_int(reader, 4)
    data = await reader.readexactly(length)
    return data.decode(encoding)

class RFBDes(pyDes.des):
    def setKey(self, key: bytes) -> None:
        """RFB protocol for authentication requires client to encrypt
           challenge sent by server with password using DES method. However,
           bits in each byte of the password are put in reverse order before
           using it as encryption key."""
        newkey = bytes(
            sum((128 >> i) if (k & (1 << i)) else 0 for i in range(8))
            for k in key
        )
        super().setKey(newkey)

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
    async def intro(self):
        intro = await self.reader.readline()
        if intro[:4] != b'RFB ':
            raise ValueError(f'not a VNC server: {intro}')
        self.writer.write(b'RFB 003.008\n')

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
            reason = await read_text(self.reader, "latin-1")
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
        padding = int(0)
        self.writer.write(padding.to_bytes(1, "big"))
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

        name = await read_text(self.reader, "latin-1")

        return w,h

async def test(func, times = 5, sleepTime = 2):
    result = True
    client = Client()
    await client.connect(host, port)
    await client.intro()
    result = await client.security("popo")
    if result == False:
        return
    await client.clientInit()
    w,h = await client.ServerInit()
    await func(client, w, h)
    try:
        for i in range(times):
            if client.writer.is_closing():
                raise Exception("closing")
            print("tick")
            await client.framebufferUpdateRequest(False, 0, 0, w, h)
            # read image?
            await sleep(sleepTime)
    except Exception as e:
        print(f"Exception: {e}")
        result = False
    
    await client.disconnect()
    return result

# SetEncoding
async def setEncodingUnderflow(client: Client, w, h):
    await client.setEncodings(0, [1,2,3,4,5,6])

async def setEncodingOverflow(client: Client, w, h):
    await client.setEncodings(200, [1,2])

# FramebufferUpdateRequest
async def frameRequestInvalidPos(client: Client, w, h):
    await client.framebufferUpdateRequest(False, 8430, 4578, w, h)

async def frameRequestInvalidWidth(client: Client, w, h):
    await client.framebufferUpdateRequest(False, 0, 0, 8603, 8301)

# KeyEvent
async def keyEventInvalidKey(client: Client, w, h):
    await client.keyEvent(True, 0xFFFFFFFF)

# PointerEvent
async def pointerEventInvalidPos(client: Client, w, h):
    await client.pointerEvent(0b00000000, 8304, 8301)

# ClientCutText
async def clientCutTextUnderflow(client: Client, w, h):
    await client.clientCutText(5, "0"*50)

async def clientCutTextOverflow(client: Client, w, h):
    await client.clientCutText(200, "0")

# Invalid Packet
async def invalidPackets(client: Client, w, h):
    for i in range(7):
        await client.rawEvent(i, [(1,2),(2,3),(3,4),(4,5),(5,6)])

# Out of order packet
async def outOfOrderProtocol(client: Client, w, h):
    await client.intro()

async def outOfOrderClientInit(client: Client, w, h):
    await client.clientInit()

async def outOfOrderSecurity(client: Client, w, h):
    await client.security("1234")

async def outOfOrderAuthenticate(client: Client, w, h):
    await client.authenticate(2, "1234")

tests = [
    setEncodingUnderflow,
    setEncodingOverflow,

    frameRequestInvalidPos,
    frameRequestInvalidWidth,

    keyEventInvalidKey,

    pointerEventInvalidPos,

    clientCutTextUnderflow,
    clientCutTextOverflow,

    invalidPackets,

    outOfOrderProtocol,
    outOfOrderClientInit,
    outOfOrderAuthenticate,
    outOfOrderSecurity
]

from tabulate import tabulate
async def main():
    results = []
    for t in tests:
        name = t.__qualname__
        print(name)
        results.append([name, await test(t)])
        await sleep(1)
    print(tabulate(results, headers=["Function", "Result"], tablefmt="grid"))

run(main()) # TODO