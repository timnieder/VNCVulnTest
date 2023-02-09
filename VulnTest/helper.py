from asyncio import StreamReader

async def read_int(reader: StreamReader, length: int) -> int:
    """
    Reads, unpacks, and returns an integer of *length* bytes.
    """

    return int.from_bytes(await reader.readexactly(length), 'big')

async def read_text(reader: StreamReader, encoding: str = "latin-1") -> str:
    """
    Reads, unpacks, and returns length-prefixed text.
    """

    length = await read_int(reader, 4)
    data = await reader.readexactly(length)
    return data.decode(encoding)

async def read_bool(reader: StreamReader, length: int) -> bool:
    """
    Reads, unpacks, and returns an boolean of *length* bytes.
    """

    return bool.from_bytes(await reader.readexactly(length), 'big')

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