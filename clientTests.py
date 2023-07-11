from client import Client

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

async def pixelFormatZero(client: Client, w, h):
    from pixelFormat import PixelFormat
    client.pixelFormat = PixelFormat(32, 24, False, False, 0,0,0,0,0,0)
    await client.setPixelFormat(client.pixelFormat)

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
    outOfOrderSecurity,

    pixelFormatZero,
]