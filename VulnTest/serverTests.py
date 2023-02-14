from server import Server, generateRawData
from helper import read_int
from asyncio import StreamReader, StreamWriter
from const import SecurityResult, SecurityTypes

async def rfc(server: Server):
    valid = await server.intro()
    if valid == False:
        raise Exception("not a rfb client")
    auth_type = await server.security(1, [SecurityTypes.VNC])
    authed = True
    if auth_type == SecurityTypes.VNC:
        authed = await server.vncAuth("1234")
    result = SecurityResult.FAILED
    if authed == True:
        result = SecurityResult.OK
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

# Intro
async def overlongIntro(server: Server):
    valid = await server.intro(b'a'*600)
    auth_type = await server.security(1, [SecurityTypes.NONE])

async def shortIntro(server: Server):
    valid = await server.intro(b'\n')
    auth_type = await server.security(1, [SecurityTypes.NONE])

# Security Handshake
async def securityUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE,SecurityTypes.VNC,3,4,5,6,7,8,9,1,2,3,34,5,4,3])
    await server.securityResult(SecurityResult.OK)

async def securityOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(20, [SecurityTypes.NONE])

async def securityReasonUnderflow(server: Server):
    valid = await server.intro()
    await server.failedSecurity(0, [], 3, "a"*500)
    await server.clientInit()

async def securityReasonOverflow(server: Server):
    valid = await server.intro()
    await server.failedSecurity(0, [], 300, "failed")
    await server.clientInit()

# VNC Auth
async def vncAuthChallengeUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.VNC])
    # write invalid challenge
    import secrets
    challenge = secrets.token_bytes(1)
    server.writer.write(challenge)
    clientRes = await server.reader.readexactly(16)
    await server.securityResult(SecurityResult.OK)

async def vncAuthChallengeOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.VNC])
    # write invalid challenge
    import secrets
    challenge = secrets.token_bytes(256)
    server.writer.write(challenge)
    clientRes = await server.reader.readexactly(16)
    await server.securityResult(SecurityResult.OK)

# Security Result
async def securityResultReasonUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.FAILED)
    await server.securityResultReason(1, "a"*500)

async def securityResultReasonOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.FAILED)
    await server.securityResultReason(500, "failed")

# ServerInit
async def serverInitUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 1, "a"*500)
    await server.serverCutText(4, "text")

async def serverInitOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 500, "name")
    await server.serverCutText(4, "text")

# FramebufferUpdate
async def frameBufferSetup(server: Server, callback):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == 0:
            pixelFormat = await server.setPixelFormat()
        elif message_type == 2:
            encodings = await server.setEncodings()
        elif message_type == 3:
            incremental, x, y, w, h = await server.framebufferUpdateRequest()
            # send malicious data back
            await callback(server)
        elif message_type == 4:
            down, key = await server.keyEvent()
        elif message_type == 5:
            mask, x, y = await server.pointerEvent()
        elif message_type == 6:
            text = await server.clientCutText()
        else:
            print(f"unknown message type {message_type}")

async def frameBufferRectanglesUnderflow(server: Server):
    async def callback(server: Server):
        data = await generateRawData(server.width, server.height, server.pixelFormat)
        await server.framebufferUpdate(1, [(0, 0, server.width, server.height, 0), (0, 0, server.width, server.height, 0), (0, 0, server.width, server.height, 0)], [data,data,data])
    await frameBufferSetup(server, callback)

async def frameBufferRectanglesOverflow(server: Server):
    async def callback(server: Server):
        data = await generateRawData(server.width, server.height, server.pixelFormat)
        await server.framebufferUpdate(300, [(0, 0, server.width, server.height, 0)], [data])
    await frameBufferSetup(server, callback)

async def frameBufferXYWHUnderflow(server: Server):
    async def callback(server: Server):
        #x = -server.width - 500
        #y = -server.height - 500
        x = 60000
        y = 60000
        data = await generateRawData(server.width, server.height, server.pixelFormat)
        await server.framebufferUpdate(1, [(x, y, server.width, server.height, 0)], [data], False)
    await frameBufferSetup(server, callback)

async def frameBufferXYWHOverflow(server: Server):
    async def callback(server: Server):
        x = server.width + 500
        y = server.height + 500
        data = await generateRawData(server.width, server.height, server.pixelFormat)
        await server.framebufferUpdate(1, [(x, y, server.width, server.height, 0)], [data])
    await frameBufferSetup(server, callback)

async def frameBufferRawDataUnderflow(server: Server):
    async def callback(server: Server):
        data = await generateRawData(int(server.width/2), int(server.height/2), server.pixelFormat)
        await server.framebufferUpdate(1, [(0, 0, server.width, server.height, 0)], [data])
    await frameBufferSetup(server, callback)

async def frameBufferRawDataOverflow(server: Server):
    async def callback(server: Server):
        data = await generateRawData(server.width, server.height, server.pixelFormat)
        await server.framebufferUpdate(1, [(0, 0, int(server.width/2), int(server.height/2), 0)], [data*5])
    await frameBufferSetup(server, callback)

# TODO: other encodings?

# SetColorMapEntries
async def setColorMapEntriesIndexUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    color = (255, 255, 255)
    await server.setColorMapEntries(-1000, 5, [color,color,color,color,color])

async def setColorMapEntriesIndexOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    color = (255, 255, 255)
    await server.setColorMapEntries(2000, 5, [color,color,color,color,color])

async def setColorMapEntriesNumUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    color = (255, 255, 255)
    await server.setColorMapEntries(0, 1, [color,color,color,color,color])

async def setColorMapEntriesNumOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    color = (255, 255, 255)
    await server.setColorMapEntries(0, 600, [color])

# ServerCutText
async def serverCutTextUnderflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    await server.serverCutText(1, "a"*500)

async def serverCutTextOverflow(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "desktop")
    await server.serverCutText(600, "text")


tests = [
    overlongIntro,
    #shortIntro, # client doesnt answer

    securityUnderflow,
    #securityOverflow,
    securityReasonUnderflow,
    #securityReasonOverflow,

    #vncAuthChallengeUnderflow,
    vncAuthChallengeOverflow,

    securityResultReasonUnderflow,
    securityResultReasonOverflow,

    serverInitUnderflow,
    serverInitOverflow,

    frameBufferRectanglesUnderflow,
    frameBufferRectanglesOverflow,
    frameBufferXYWHUnderflow,
    frameBufferXYWHOverflow,
    frameBufferRawDataUnderflow,
    frameBufferRawDataOverflow,

    setColorMapEntriesIndexUnderflow,
    setColorMapEntriesIndexOverflow,

    serverCutTextUnderflow,
    serverCutTextOverflow
]