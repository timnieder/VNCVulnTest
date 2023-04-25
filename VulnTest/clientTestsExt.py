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
    await client.setEncodings(2, [Encodings.Raw, PseudoEncodings.FTProcolVersion])
    await client.setPixelFormat(client.pixelFormat)
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

# lib, ultra
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

async def giiViewOnly(client: Client):
    await client.intro()
    result = await client.security("viewonly")
    if result == False:
        print("wrong pw")
        return
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.ZRLE, PseudoEncodings.gii])
    await client.setPixelFormat(client.pixelFormat)
    # parse client messages
    while True:
        message_type = await read_int(client.reader, 1, False)
        if message_type == S2CMessages.FramebufferUpdate:
            update = await client.framebufferUpdate(client.pixelFormat)
        elif message_type == S2CMessages.SetColorMapEntries:
            encodings = await client.setColorMapEntries()
        elif message_type == S2CMessages.Bell:
            await client.bell()
        elif message_type == S2CMessages.ServerCutText:
            text = await client.serverCutText()
        elif message_type == S2CMessages.gii:
            print(f"gii: {message_type}")
            endianess, type, data = await client.gii()
            print(f"endianess: {endianess}, type: {type}, data:")
            print(data)
            if type == 1: #version
                print("version")
                # send version
                data = int(1).to_bytes(2, "big")
                await client.sendGii(129, len(data), data)
                #create device
                data = bytes()
                name = "device" # max 31 chars
                data += name.encode("latin-1")
                data += int(0).to_bytes(32 - len(name), "big") # pad to 32
                data += int(0).to_bytes(4, "big") # vendor
                data += int(0).to_bytes(4, "big") # product
                data += int(0).to_bytes(4, "big") # can-generate
                data += int(0).to_bytes(4, "big") # num-registers
                data += int(1).to_bytes(4, "big") # num-valuators
                data += int(1).to_bytes(4, "big") # num buttons
                data += int(0).to_bytes(116, "big") # valuator
                await client.sendGii(130, len(data), data)
            elif type == 2: # device creation
                print("device creation")
                origin = int.from_bytes(data[0:4], "big")
                print(f"origin: {origin}")
                data = bytes()
                count = 1
                first = 1
                data += int(16 + 4 * count).to_bytes(1, "big") # event-size
                data += int(12).to_bytes(1, "big") # event-type
                data += int(0).to_bytes(2, "big") # padding
                data += origin.to_bytes(4, "big") # origin
                data += first.to_bytes(4, "big") # first
                data += count.to_bytes(4, "big") # count

                # flags: position, pressed/down
                flag = 0 | 0x10 | 0x80000000
                data += flag.to_bytes(4, "big") # flag
                data += int(0).to_bytes(4, "big") # id
                pos = bytes()
                pos += int(100).to_bytes(2, "big") # x
                pos += int(100).to_bytes(2, "big") # y
                data += pos # pos

                await client.sendGii(128, len(data), data)
        else:
            print(f"unknown message: {message_type}")#

# lib, ultra
async def setScaleFactorZero(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScaleFactor(0)

async def setScaleFactorNegative(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScaleFactor(-128, True)

async def setScaleFactorMax(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    await client.setPixelFormat(client.pixelFormat)
    await client.setScaleFactor(255)

# lib, ultra
async def SW(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    await client.setPixelFormat(client.pixelFormat)
    await client.SetSW(0, -1, -1, signed=True)

# tight, lib, ultra
async def TextChatOverlong(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    await client.setPixelFormat(client.pixelFormat)
    # open twice
    length = 65500
    data = length*b"\x00"
    await client.TextChat(length, data)

# lib, ultra
async def SetDesktopSize(client: Client):
    await client.intro()
    result = await client.security("12345678")
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [Encodings.RRE, Encodings.Raw])
    from pixelFormat import PixelFormat
    client.pixelFormat = PixelFormat(32, 24, True,True,0,0,0,0,0,0)
    await client.setPixelFormat(client.pixelFormat)
    w = -1
    h = -1
    await client.SetDesktopSize(w, h, 1, [(1, w, h, w, h, 0)], signed=True)


tests = [
    #xvpViewOnly,
    #setScaleZero,
    #setScaleNegative,
    #setScaleMax,
    #giiViewOnly,
    #setScaleFactorZero,
    #setScaleFactorNegative,
    #setScaleFactorMax,
    #SW,
    #TextChatOverlong,
    #SetDesktopSize,
    ServerState
]