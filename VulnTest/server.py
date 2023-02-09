from asyncio import StreamReader, StreamWriter, open_connection, run, sleep, start_server
from dataclasses import field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # pip install cryptography
from rfbDes import RFBDes # rfbDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
from tabulate import tabulate
import secrets

class PixelFormat:
    bitsPerPixel: int = field()
    depth: int = field()
    bigEndian: bool = field()
    trueColor: bool = field()
    redMax: int = field()
    greenMax: int = field()
    blueMax: int = field()
    redShift: int = field()
    greenShift: int = field()
    blueShift: int = field()

    def __init__(self, bpp, d, big, true, rMax, gMax, bMax, rShift, gShift, bShift):
        self.bitsPerPixel = bpp
        self.depth = d
        self.bigEndian = big
        self.trueColor = true
        self.redMax = rMax
        self.greenMax = gMax
        self.blueMax = bMax
        self.redShift = rShift
        self.greenShift = gShift
        self.blueShift = bShift

    def __str__(self):
        return f"""bits-per-pixel: {self.bitsPerPixel}
depth: {self.depth}
big-endian-flag: {self.bigEndian}
true-color-flag: {self.trueColor}
red-max: {self.redMax}
green-max: {self.greenMax}
blue-max: {self.blueMax}
red-shift: {self.redShift}
green-shift: {self.greenShift}
blue-shift: {self.blueShift}"""

async def read_int(reader: StreamReader, length: int) -> int:
    """
    Reads, unpacks, and returns an integer of *length* bytes.
    """

    return int.from_bytes(await reader.readexactly(length), 'big')

async def read_bool(reader: StreamReader, length: int) -> bool:
    """
    Reads, unpacks, and returns an boolean of *length* bytes.
    """

    return bool.from_bytes(await reader.readexactly(length), 'big')

async def read_text(reader: StreamReader, encoding: str = "latin-1") -> str:
    """
    Reads, unpacks, and returns length-prefixed text.
    """

    length = await read_int(reader, 4)
    data = await reader.readexactly(length)
    return data.decode(encoding)

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

async def pixelformat2bytes(format: PixelFormat) -> bytes:
    msg = bytes()
    msg += format.bitsPerPixel.to_bytes(1, "big") # bits per pixel
    msg += format.depth.to_bytes(1, "big") # depth
    msg += format.bigEndian.to_bytes(1, "big") # big endian
    msg += format.trueColor.to_bytes(1, "big") # true color
    msg += format.redMax.to_bytes(2, "big") # red max
    msg += format.greenMax.to_bytes(2, "big") # green max
    msg += format.blueMax.to_bytes(2, "big") # blue max
    msg += format.redShift.to_bytes(1, "big") # red shift
    msg += format.greenShift.to_bytes(1, "big") # green shift
    msg += format.blueShift.to_bytes(1, "big") # blue shift
    return msg

async def read_pixelformat(reader: StreamReader) -> PixelFormat:
    bpp = await read_int(reader, 1)
    depth = await read_int(reader, 1)
    bigEndian = await read_bool(reader, 1)
    trueColor = await read_bool(reader, 1)
    redMax = await read_int(reader, 2)
    greenMax = await read_int(reader, 2)
    blueMax = await read_int(reader, 2)
    redShift = await read_int(reader, 1)
    greenShift = await read_int(reader, 1)
    blueShift = await read_int(reader, 1)
    padding = await reader.readexactly(3)
    return PixelFormat(bpp, depth, bigEndian, trueColor, redMax, greenMax, blueMax, redShift, greenShift, blueShift)

def rawColor(r, g, b, format) -> int:
    return ((r & format.redMax) << format.redShift) | ((g & format.greenMax) << format.greenShift) | ((b & format.blueMax) << format.blueShift)

# black white pattern #TODO: more like black and yellow
async def generateRawData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    black = rawColor(0, 0, 0, format)
    white = rawColor(255, 255, 255, format)
    alternate = True
    bpp = int(format.bitsPerPixel / 8)
    endianess = "big"
    for i in range(w):
        for j in range(h):
            if alternate:
                clr = black
            else:
                clr = white
            alternate = not alternate
            msg += clr.to_bytes(bpp, endianess)
    return msg


class Server:
    reader: StreamReader = field(repr=False)
    writer: StreamWriter = field(repr=False)
    width: int = field()
    height: int = field()
    pixelFormat: PixelFormat = field()

    def __init__(self, w: int, h: int, format: PixelFormat) -> None:
        self.width = w
        self.height = h
        self.pixelFormat = format

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

    async def clientInit(self) -> bool:
        return await read_bool(self.reader, 1)

    async def serverInit(self, w: int, h: int, format: PixelFormat, nameLength: int, name: str):
        msg = bytes()
        msg += w.to_bytes(2, "big")
        msg += h.to_bytes(2, "big")
        # pixelformat
        msg += await pixelformat2bytes(format)
        # padding
        msg += int(0).to_bytes(3, "big")
        # length
        msg += await text2bytes(nameLength, name)
        self.writer.write(msg)

    # c2s messages # skip reading message type as its probably read beforehand
    async def setPixelFormat(self) -> PixelFormat: # 0
        await self.reader.readexactly(3) # padding
        return await read_pixelformat(self.reader) # pixel-format

    async def setEncodings(self) -> List[int]: # 2
        encodings = []
        await self.reader.readexactly(1) # padding
        num = await read_int(self.reader, 2) # number-of-encodings
        for i in range(num):
            encoding = await read_int(self.reader, 4) # encoding-type
            encodings.append(encoding)
        return encodings

    async def framebufferUpdateRequest(self) -> Tuple[bool, int, int, int, int]: # 3
        incremental = await read_bool(self.reader, 1)
        x = await read_int(self.reader, 2)
        y = await read_int(self.reader, 2)
        w = await read_int(self.reader, 2)
        h = await read_int(self.reader, 2)
        return incremental, x, y, w, h

    async def keyEvent(self) -> Tuple[bool, int]: # 4
        down = await read_bool(self.reader, 1)
        await self.reader.readexactly(2) # padding
        key = await read_int(self.reader, 4)
        return down, key

    async def pointerEvent(self) -> Tuple[int, int, int]: # 5
        mask = await read_int(self.reader, 1)
        x = await read_int(self.reader, 2)
        y = await read_int(self.reader, 2)
        return mask, x, y

    async def clientCutText(self) -> str: # 6
        await self.reader.readexactly(3) # padding
        text = await read_text(self.reader)
        return text

    # s2c messages
    async def framebufferUpdate(self, num, rectangles:Collection[Tuple[int, int, int, int, int]], pixelData:Collection[bytes]):
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

async def rfc(server: Server, reader: StreamReader, writer: StreamWriter):
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
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")
    
    # parse client messages
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == 0:
            pixelFormat = await server.setPixelFormat()
            print(f"SetPixelFormat: {pixelFormat}")
        elif message_type == 2:
            encodings = await server.setEncodings()
            print(f"Encodings: {encodings}")
        elif message_type == 3:
            incremental, x, y, w, h = await server.framebufferUpdateRequest()
            # send random data back
            data = await generateRawData(server.width, server.height, server.pixelFormat)
            await server.framebufferUpdate(1, [(0, 0, server.width, server.height, 0)], [data])
        elif message_type == 4:
            down, key = await server.keyEvent()
        elif message_type == 5:
            mask, x, y = await server.pointerEvent()
        elif message_type == 6:
            text = await server.clientCutText()
        else:
            print(f"unknown message type {message_type}")
    
    print("server done")

async def test(func):
    width = 300
    height = 300
    format = PixelFormat(32, 32, False, True, 255, 255, 255, 16, 8, 0)
    server = Server(width, height, format)
    host = "127.0.0.1"
    port = 5900
    async def callback(reader, writer):
        await func(server, reader, writer)
    await server.listen(callback, host, port)

# TODO: tests
run(test(rfc))