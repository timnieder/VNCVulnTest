from asyncio import StreamReader, StreamWriter, open_connection, run, sleep, start_server
from dataclasses import field
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes # pip install cryptography
from rfbDes import RFBDes # rfbDes.py
from typing import Any, Callable, ClassVar, Collection, Iterator, List, Optional, Tuple, cast
from tabulate import tabulate
import secrets
from helper import read_bool, read_int, read_text, text2bytes
from const import SecurityResult, SecurityTypes, C2SMessages, S2CMessages
import struct
import bitstring
import zlib
from pixelFormat import PixelFormat, pixelformat2bytes, read_pixelformat

def rawColor(r, g, b, format) -> int:
    return ((r & format.redMax) << format.redShift) | ((g & format.greenMax) << format.greenShift) | ((b & format.blueMax) << format.blueShift)

# encoding 0
# black white pattern
async def generateRawData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    black = rawColor(0, 0, 0, format)
    white = rawColor(255, 255, 255, format)
    alternate = True
    bpp = int(format.bitsPerPixel / 8)
    endianess = "big" if format.bigEndian else "little"
    for i in range(w):
        for j in range(h):
            if alternate:
                clr = black
            else:
                clr = white
            alternate = not alternate
            msg += clr.to_bytes(bpp, endianess)
    return msg

# encoding 1
async def copyRect(srcX: int, srcY: int, signed=False) -> bytes:
    msg = bytes()
    msg += srcX.to_bytes(2, "big", signed=signed)
    msg += srcY.to_bytes(2, "big", signed=signed)
    return msg

# encoding 2
# chessboard, 2 subrectangles
async def generateRREData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    bpp = int(format.bitsPerPixel / 8)
    endianess = "big" if format.bigEndian else "little"
    black = rawColor(0, 0, 0, format)
    white = rawColor(255, 255, 255, format)
    # header
    msg += int(2).to_bytes(4, "big", signed=False) #number-of-subrectangles
    msg += black.to_bytes(bpp, endianess) # background-pixel-value
    # 2 subrectangles
    # first
    msg += white.to_bytes(bpp, endianess) # subrect-pixel-value
    msg += int(0).to_bytes(2, "big", signed=False) #x
    msg += int(0).to_bytes(2, "big", signed=False) #y
    msg += int(w/2).to_bytes(2, "big", signed=False) #w
    msg += int(h/2).to_bytes(2, "big", signed=False) #h
    # second
    msg += white.to_bytes(bpp, endianess) # subrect-pixel-value
    msg += int(w/2).to_bytes(2, "big", signed=False) #x
    msg += int(h/2).to_bytes(2, "big", signed=False) #y
    msg += int(w/2).to_bytes(2, "big", signed=False) #w
    msg += int(h/2).to_bytes(2, "big", signed=False) #h
    return msg

def hextileMask(raw: bool, background: bool, foreground: bool, anySubrects: bool, subrectsColored: bool) -> int:
    return (int(raw) << 0) | (int(background) << 1) | (int(foreground) << 2) | (int(anySubrects) << 3) | (int(subrectsColored) << 4)

def hextileSubrect(x: int, y: int, w: int, h: int) -> bytes:
    return struct.pack(">BB", (x << 4 | y << 0), ((w-1) << 4 | (h-1) << 0))

# encoding 5
async def generateHextileData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    bpp = int(format.bitsPerPixel / 8)
    endianess = "big" if format.bigEndian else "little"
    black = rawColor(0, 0, 0, format)
    white = rawColor(255, 255, 255, format)
    red = rawColor(255, 0, 0, format)
    blue = rawColor(0, 0, 255, format)
    sizeW = 16
    sizeH = 16
    wLeft = w
    hLeft = h
    startI = 0
    endI = 4
    i = startI
    while (hLeft > 0):
        while (wLeft > 0):
            # cope with the size
            rectW = min(sizeW, wLeft)
            rectH = min(sizeH, hLeft)
            rectangle = bytes()
            if (i == 0): # raw
                rectangle += hextileMask(True, False, False, False, False).to_bytes(1, "big")
                rectangle += await generateRawData(rectW, rectH, format)
            elif (i == 1): # background, black
                rectangle += hextileMask(False, True, False, False, False).to_bytes(1, "big")
                rectangle += black.to_bytes(bpp, endianess)
            elif (i == 2): # foreground, 1 subrects, fully white
                rectangle += hextileMask(False, False, True, True, False).to_bytes(1, "big")
                rectangle += white.to_bytes(bpp, endianess)
                rectangle += int(1).to_bytes(1, "big", signed=False) #number of subrects
                rectangle += hextileSubrect(0, 0, rectW, rectH)
            elif (i == 3): # 2 subrects, depend on fg clr
                rectangle += hextileMask(False, False, False, True, False).to_bytes(1, "big")
                rectangle += int(2).to_bytes(1, "big", signed=False) #number of subrects
                rectangle += hextileSubrect(0, 0, int(rectW/2), int(rectH/2))
                rectangle += hextileSubrect(int(rectW/2),int(rectH/2), int(rectW/2), int(rectH/2))
            elif (i == 4): # 2 subrects, diff colors
                rectangle += hextileMask(False, False, False, True, True).to_bytes(1, "big")
                rectangle += int(2).to_bytes(1, "big", signed=True) #number of subrects
                rectangle += red.to_bytes(bpp, endianess)
                rectangle += hextileSubrect(0,0, int(rectW/2), int(rectH/2))
                rectangle += blue.to_bytes(bpp, endianess)
                rectangle += hextileSubrect(int(rectW/2),int(rectH/2), int(rectW/2), int(rectH/2))
            wLeft -= sizeW
            msg += rectangle
        hLeft -= sizeH
        wLeft = w
        i += 1 # cycle i
        if (i > endI): # reset i
            i = startI
    return msg

# generates a packedpalette tile by alternating the colors
def packedPalette(colors, rectH, rectW, bpp, endianess, reuse=False):
    tile = bytes()
    paletteSize = len(colors)
    if (reuse):
        tile += int(127).to_bytes(1, "big")
    else:
        tile += int(paletteSize).to_bytes(1, "big")
        for clr in colors:
            tile += clr.to_bytes(bpp, endianess)
    j = 0
    length = 1
    if (paletteSize >= 3):
        length = 2
    if (paletteSize >= 5):
        length = 4
    for x in range(rectH):
        bits = bitstring.BitArray()
        count = 0 # count how many bits we've added
        for y in range(rectW):
            bits.append(bitstring.Bits(uint=j, length=length))
            count += length
            j += 1 # cycle palette index
            if j == paletteSize: # reset palette index
                j = 0
        if (count % 8 != 0): # pad to a full byte at the end of the row
            bits.append(bitstring.Bits(uint=0, length=(count % 8))) # missing bits
        tile += bits.bytes
    return tile

def RLELength(length) -> bytes:
    l = length - 1
    arr = bytes()
    for i in range(int(l / 255)):
        arr += int(255).to_bytes(1, "big")
    arr += int(l % 255).to_bytes(1, "big")
    return arr

# encoding 15
async def generateTRLEData(w: int, h: int, format: PixelFormat, allowReuse=True, sizeW=16, sizeH=16) -> bytes:
    msg = bytes()
    bpp = int(format.bitsPerPixel / 8)
    if (format.trueColor != False and format.bitsPerPixel == 32 and format.depth <= 24):
        bpp = 3 # cpixel fits into 3 bytes
    endianess = "big" if format.bigEndian else "little"
    black = rawColor(0, 0, 0, format)
    white = rawColor(255, 255, 255, format)
    red = rawColor(255, 0, 0, format)
    green = rawColor(0, 255, 0, format)
    blue = rawColor(0, 0, 255, format)
    wLeft = w
    hLeft = h
    startI = 0
    endI = 8
    i = startI
    while (hLeft > 0):
        while (wLeft > 0):
            # cope with the size
            rectW = min(sizeW, wLeft)
            rectH = min(sizeH, hLeft)
            rectangle = bytes()
            if (i == 0): # raw, alternating black white
                rectangle += int(0).to_bytes(1, "big")
                alternate = True
                for x in range(rectW):
                    for y in range(rectH):
                        if alternate:
                            clr = black
                        else:
                            clr = white
                        alternate = not alternate
                        rectangle += clr.to_bytes(bpp, endianess)
            elif (i == 1): # solid tile
                rectangle += int(1).to_bytes(1, "big")
                rectangle += white.to_bytes(bpp, endianess)
            elif (i == 2): # packed palette, 2 colors
                rectangle += packedPalette([red, green], rectH, rectW, bpp, endianess)
            elif (i == 3): # packed palette, 3 colors
                rectangle += packedPalette([red, green, blue], rectH, rectW, bpp, endianess)
            elif (i == 4): # packed palette, 4 colors
                rectangle += packedPalette([red, green, blue, white], rectH, rectW, bpp, endianess)
            elif (i == 5): # reuse palette
                rectangle += packedPalette([red, green, blue, white], rectH, rectW, bpp, endianess, True)
            elif (i == 6): # plain RLE, striped black and white
                rectangle += int(128).to_bytes(1, "big")
                length = RLELength(int((rectW * rectH) / 2))
                rectangle += black.to_bytes(bpp, endianess)
                rectangle += length
                rectangle += white.to_bytes(bpp, endianess)
                rectangle += length
            elif (i == 7): # palette RLE, 2 colors
                rectangle += int(130).to_bytes(1, "big")
                rectangle += red.to_bytes(bpp, endianess)
                rectangle += blue.to_bytes(bpp, endianess)
                rectangle += int(0).to_bytes(1, "big") # 1 red pixel
                rectangle += int(1 + 128).to_bytes(1, "big") # fill with blue
                length = int((rectW * rectH) / 2)
                rectangle += RLELength(length - 1)
                rectangle += int(0 + 128).to_bytes(1, "big") # the rest red
                rectangle += RLELength(length)
            elif (i == 8): # palette RLE, reuse palette
                rectangle += int(129).to_bytes(1, "big")
                rectangle += int(1).to_bytes(1, "big") # 1 blue pixel
                rectangle += int(0 + 128).to_bytes(1, "big") # fill with red
                length = int((rectW * rectH) / 2)
                rectangle += RLELength(length - 1)
                rectangle += int(1 + 128).to_bytes(1, "big") # the rest blue
                rectangle += RLELength(length)
            wLeft -= sizeW
            msg += rectangle
        hLeft -= sizeH
        wLeft = w
        i += 1 # cycle i
        if not allowReuse and i in [5,8]: # skip reuse prompts for ZRLE
            i += 1
        if (i > endI): # reset i
            i = startI
    return msg

# encoding 16
zlibCompress = zlib.compressobj()
async def generateZRLEData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    data = await generateTRLEData(w, h, format, False, 64, 64)
    compressed = zlibCompress.compress(data)
    compressed += zlibCompress.flush(zlib.Z_SYNC_FLUSH)
    msg += len(compressed).to_bytes(4, "big")
    msg += compressed
    return msg

# pseudo encoding -239
async def generateCursorData(w: int, h: int, format: PixelFormat) -> bytes:
    msg = bytes()
    # generate the cursor pixels
    msg += await generateRawData(w, h, format)
    # then the bitmask
    alternate = True
    for x in range(w):
        bits = bitstring.BitArray()
        count = 0 # count how many bits we've added
        for y in range(h):
            bits.append(bitstring.Bits(bool=alternate, length=1))
            count += 1
            alternate = not alternate
        if (count % 8 != 0): # pad to a full byte at the end of the row
            bits.append(bitstring.Bits(uint=0, length=(count % 8))) # missing bits
        msg += bits.bytes
    return msg

class Server:
    reader: StreamReader = field(repr=False)
    writer: StreamWriter = field(repr=False)
    width: int = field()
    height: int = field()
    pixelFormat: PixelFormat = field()
    server = field()

    def __init__(self, w: int, h: int, format: PixelFormat) -> None:
        self.width = w
        self.height = h
        self.pixelFormat = format

    async def listen(self, callback, host = "127.0.0.1", port = 5900):
        self.server = await start_server(callback, host, port)
        print(f"serving on {host}:{port}")
        async with self.server:
            await self.server.serve_forever()
    
    async def disconnect(self):
        if not self.writer.is_closing():
            self.writer.close()
            await self.writer.wait_closed()

    async def intro(self, bytes=b'RFB 003.008\n') -> bool:
        self.writer.write(bytes)
        intro = await self.reader.readline()
        if intro[:4] != b'RFB ':
            return False
        return True

    async def security(self, num, types: Collection[SecurityTypes]) -> int:
        msg = bytes()
        msg += num.to_bytes(1, "big")
        for type in types:
            msg += int(type).to_bytes(1, "big")
        self.writer.write(msg)
        return await read_int(self.reader, 1)
    
    async def failedSecurity(self, num, types: Collection[SecurityTypes], reasonLength, reason):
        msg = bytes()
        msg += num.to_bytes(1, "big")
        for type in types:
            msg += int(type).to_bytes(1, "big")
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

    async def securityResult(self, result: SecurityResult):
        self.writer.write(int(result).to_bytes(4, "big"))

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
    async def framebufferUpdate(self, num, rectangles:Collection[Tuple[int, int, int, int, int]], pixelData:Collection[bytes], signed: bool=True):
        msg = bytes()
        message_type = 0
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += num.to_bytes(2, "big")
        for i in range(len(rectangles)):
            # rectangle
            rectangle = rectangles[i]
            msg += rectangle[0].to_bytes(2, "big", signed=signed) # x
            msg += rectangle[1].to_bytes(2, "big", signed=signed) # y
            msg += rectangle[2].to_bytes(2, "big", signed=signed) # w
            msg += rectangle[3].to_bytes(2, "big", signed=signed) # h
            msg += rectangle[4].to_bytes(4, "big", signed=True) # encoding-type
            # pixel data
            data = pixelData[i]
            msg += data
        self.writer.write(msg)

    async def setColorMapEntries(self, colorIndex: int, num: int, colors: Collection[Tuple[int, int, int]]):
        msg = bytes()
        message_type = 1
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += padding.to_bytes(1, "big")
        msg += colorIndex.to_bytes(2, "big", signed=True) # first-color
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
        message_type = int(S2CMessages.FileTransfer)
        msg += message_type.to_bytes(1, "big")
        padding = int(0)
        msg += contentType.to_bytes(1, "big")
        msg += contentParam.to_bytes(1, "big")
        msg += padding.to_bytes(1, "big")
        msg += size.to_bytes(4, "big")
        msg += length.to_bytes(4, "big")
        msg += data
        self.writer.write(msg)