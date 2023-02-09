from server import Server, generateRawData
from helper import read_int
from asyncio import StreamReader, StreamWriter

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



tests = [

]