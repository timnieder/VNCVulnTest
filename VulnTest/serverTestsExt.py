from server import Server, generateRREData
from const import C2SMessages, Encodings, PseudoEncodings, SecurityTypes, SecurityResult
from helper import read_int
from asyncio import sleep

# lib
async def ServerIdentityMax(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            length = 65535
            data = b"\x00"*length
            await server.framebufferUpdate(1, [
                (0,0,length,0,
                    PseudoEncodings.ServerIdentity)], [(data)], signed=False, encSigned=False)

# lib, ultra, tight
async def PointerPosOOR(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            x = 65535
            y = 65535
            await server.framebufferUpdate(1, [
                (x,y,0,0, PseudoEncodings.PointerPos)], [bytes()], signed=False, encSigned=False)

# lib, tight, ultra
async def ExtDesktopSizeScreenXY(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            w = 500
            h = 500
            data = bytes()
            data += int(1).to_bytes(1, "big") # number-of-screens
            data += int(0).to_bytes(3, "big") # padding
            # screen 0
            data += int(1).to_bytes(4, "big") # id
            data += int(w*2).to_bytes(2, "big") #x
            data += int(h*2).to_bytes(2, "big") #y
            data += int(w).to_bytes(2, "big") #w
            data += int(h).to_bytes(2, "big") #h
            data += int(0).to_bytes(4, "big") #flags

            await server.framebufferUpdate(1, [
                (0,0,w,h, PseudoEncodings.ExtendedDesktopSize)], 
                [data], signed=False)

            for i in range(5):
                data = await generateRREData(w, h, server.pixelFormat)
                await server.framebufferUpdate(1, [(w*2, h*2, w, h, Encodings.RRE)], [data], signed=False)
                print("tick")
                await sleep(2)
            
            break

async def ExtDesktopSizeScreenWH(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            w = 500
            h = 500

            data = bytes()
            data += int(1).to_bytes(1, "big") # number-of-screens
            data += int(0).to_bytes(3, "big") # padding
            # screen 0
            data += int(1).to_bytes(4, "big") # id
            data += int(0).to_bytes(2, "big") #x
            data += int(0).to_bytes(2, "big") #y
            data += int(w*2).to_bytes(2, "big") #w
            data += int(h*2).to_bytes(2, "big") #h
            data += int(0).to_bytes(4, "big") #flags

            await server.framebufferUpdate(1, [
                (0,0,w,h, PseudoEncodings.ExtendedDesktopSize)], 
                [data], signed=False)

            for i in range(5):
                data = await generateRREData(w, h, server.pixelFormat)
                await server.framebufferUpdate(1, [(0, 0, w*2, h*2, Encodings.RRE)], [data], signed=False)
                print("tick")
                await sleep(2)
            
            break

async def ExtDesktopSizeScreens(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            w = 500
            h = 500

            data = bytes()
            data += int(-1).to_bytes(1, "big", signed=True) # number-of-screens
            data += int(0).to_bytes(3, "big") # padding
            # screen 0
            data += int(1).to_bytes(4, "big") # id
            data += int(0).to_bytes(2, "big") #x
            data += int(0).to_bytes(2, "big") #y
            data += int(w).to_bytes(2, "big") #w
            data += int(h).to_bytes(2, "big") #h
            data += int(0).to_bytes(4, "big") #flags

            await server.framebufferUpdate(1, [
                (0,0,w,h, PseudoEncodings.ExtendedDesktopSize)], 
                [data], signed=False)

            for i in range(5):
                data = await generateRREData(w, h, server.pixelFormat)
                await server.framebufferUpdate(1, [(0, 0, w, h, Encodings.RRE)], [data], signed=False)
                print("tick")
                await sleep(2)

            break

# ultra
async def ExtendedViewSizeYX(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            w = 500
            h = 500

            await server.framebufferUpdate(1, [
                (w*30,h*30,w,h, PseudoEncodings.ExtendedViewSize)], 
                [bytes()], signed=False)

            for i in range(5):
                data = await generateRREData(w, h, server.pixelFormat)
                await server.framebufferUpdate(1, [(0, 0, w, h, Encodings.RRE)], [data], signed=False)
                print("tick")
                await sleep(2)

            break

async def ExtendedViewSizeWH(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            w = 65535
            h = 65535

            await server.framebufferUpdate(1, [
                (0,0,w,h, PseudoEncodings.ExtendedViewSize)], 
                [bytes()], signed=False)

            for i in range(5):
                data = await generateRREData(w, h, server.pixelFormat)
                await server.framebufferUpdate(1, [(0, 0, w, h, Encodings.RRE)], [data], signed=False)
                print("tick")
                await sleep(2)

            break

# lib, ultra
async def ExtendedClipboardDisabledRequest(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    sent = False
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            await server.setPixelFormat()
            #request
            if not sent:
                await server.extendedServerCutText(-4, 1|1<<25, bytes())
                print("sent ext servercuttext")
                sent = True
        elif message_type == C2SMessages.SetEncodings:
            await server.setEncodings()
        elif message_type == C2SMessages.FramebufferUpdateRequest:
            await server.framebufferUpdateRequest()
        elif message_type == C2SMessages.PointerEvent:
            await server.pointerEvent()
        elif message_type == C2SMessages.KeyEvent:
            await server.keyEvent()
        elif message_type == C2SMessages.ClientCutText:
            data = await server.clientCutText(True)
            print(data)
        else:
            print(f"unknown msg {message_type}")

#ultra
async def ServerState(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    sent = False
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            await server.setPixelFormat()
            #request
            if not sent:
                print("sending")
                await server.ServerState(2, -1, True)
                await server.ServerState(3, -1, True)
                sent = True
        elif message_type == C2SMessages.SetEncodings:
            await server.setEncodings()
        elif message_type == C2SMessages.FramebufferUpdateRequest:
            await server.framebufferUpdateRequest()
        elif message_type == C2SMessages.PointerEvent:
            await server.pointerEvent()
        elif message_type == C2SMessages.KeyEvent:
            await server.keyEvent()
        elif message_type == C2SMessages.ClientCutText:
            data = await server.clientCutText(True)
            print(data)
        else:
            print(f"unknown msg {message_type}")

#ultra, lib
async def ResizeFramebuffer(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    sent = False
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            await server.setPixelFormat()
            #request
            if not sent:
                print("sending")
                await server.ResizeFramebuffer(-1, -1, True)
                sent = True
        elif message_type == C2SMessages.SetEncodings:
            await server.setEncodings()
        elif message_type == C2SMessages.FramebufferUpdateRequest:
            await server.framebufferUpdateRequest()
        elif message_type == C2SMessages.PointerEvent:
            await server.pointerEvent()
        elif message_type == C2SMessages.KeyEvent:
            await server.keyEvent()
        elif message_type == C2SMessages.ClientCutText:
            data = await server.clientCutText(True)
            print(data)
        else:
            print(f"unknown msg {message_type}")

#ultra, lib
async def PalmVNCResizeFramebuffer(server: Server):
    valid = await server.intro()
    auth_type = await server.security(1, [SecurityTypes.NONE])
    await server.securityResult(SecurityResult.OK)
    sharedFlag = await server.clientInit()
    await server.serverInit(server.width, server.height, server.pixelFormat, 7, "Desktop")

    sent = False
    while True:
        message_type = await read_int(server.reader, 1)
        if message_type == C2SMessages.SetPixelFormat:
            await server.setPixelFormat()
            #request
            if not sent:
                print("sending")
                await server.PalmVNCResizeFramebuffer(500,500,-1, -1, True)
                await server.PalmVNCResizeFramebuffer(-1,-1,500, 500, True)
                sent = True
        elif message_type == C2SMessages.SetEncodings:
            await server.setEncodings()
        elif message_type == C2SMessages.FramebufferUpdateRequest:
            await server.framebufferUpdateRequest()
        elif message_type == C2SMessages.PointerEvent:
            await server.pointerEvent()
        elif message_type == C2SMessages.KeyEvent:
            await server.keyEvent()
        elif message_type == C2SMessages.ClientCutText:
            data = await server.clientCutText(True)
            print(data)
        else:
            print(f"unknown msg {message_type}")

tests = [
    #ServerIdentityMax,
    #PointerPosOOR,
    #ExtDesktopSizeScreenXY,
    #ExtDesktopSizeScreenWH,
    #ExtDesktopSizeScreens,
    #ExtendedViewSizeYX,
    #ExtendedViewSizeWH,
    #ExtendedClipboardDisabledRequest,
    #ServerState,
    ResizeFramebuffer,
    PalmVNCResizeFramebuffer,
]