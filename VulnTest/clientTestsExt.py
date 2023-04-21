from client import Client
from const import S2CMessages, Encodings, PseudoEncodings
from helper import read_int

async def xvpViewOnly(client: Client):
    await client.intro()
    #result = await client.security("12345678")
    result = await client.security("viewonly")
    if result == False:
        print("wrong pw")
        return
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [0, PseudoEncodings.FTProcolVersion])
    # parse client messages
    await client.sendXvp(1, 2) # v1, XVP_SHUTDOWN
    while True:
        message_type = await read_int(client.reader, 1)
        if message_type == S2CMessages.FramebufferUpdate:
            update = await client.framebufferUpdate(client.pixelFormat)
        elif message_type == S2CMessages.SetColorMapEntries:
            encodings = await client.setColorMapEntries()
        elif message_type == S2CMessages.Bell:
            await client.bell()
        elif message_type == S2CMessages.ServerCutText:
            text = await client.serverCutText()
        elif message_type == S2CMessages.xvp:
            print("xvp")
            version, message = await client.xvp()
            print(f"v {version}, code: {message}")
            await client.sendXvp(1, 2) # v1, XVP_SHUTDOWN

async def setScaleZero(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(3, [Encodings.RRE, Encodings.Raw, PseudoEncodings.xvp])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScale(0)

async def setScaleNegative(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(3, [Encodings.RRE, Encodings.Raw, PseudoEncodings.xvp])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScale(-128, True)

async def setScaleMax(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(3, [Encodings.RRE, Encodings.Raw, PseudoEncodings.xvp])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScale(255)

tests = [
    xvpViewOnly,
    setScaleZero,
    setScaleNegative,
    setScaleMax,
]