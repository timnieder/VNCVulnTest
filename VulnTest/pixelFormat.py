from dataclasses import field
from helper import read_bool, read_int
from asyncio import StreamReader, StreamWriter

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
