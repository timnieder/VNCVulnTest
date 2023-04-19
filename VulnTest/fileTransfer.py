from client import Client
from asyncio import sleep, run
from tabulate import tabulate
from helper import read_int
from const import FileTransferMessages, S2CMessages

host = "127.0.0.1"
#host = "192.168.182.5"
port = 5900
async def main():
    client = Client()
    await client.connect(host, port)
    await client.intro()
    #result = await client.security("12345678")
    result = await client.security("viewonly")
    if result == False:
        print("wrong pw")
        return
    await client.clientInit()
    w,h,format = await client.ServerInit()
    client.pixelFormat = format
    await client.setEncodings(2, [0, 0xFFFF8002])
    #await client.pointerEvent(0,0,0)
    await client.sendFileTransfer(FileTransferMessages.DirContentRequest, 2, 0, 0, bytes())
    # parse client messages
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
        elif message_type == S2CMessages.FileTransfer:
            print("FileTransfer")
            type, param, size, data = await client.fileTransfer()
            print(f"type: {type}, param: {param}")
            print(f"size: {size}")
            print(data)
            if type == FileTransferMessages.FileTransferProtocolVersion:
                print(f"File Transfer Version: {param}")
                #rfbRDrivesList
                await client.sendFileTransfer(FileTransferMessages.DirContentRequest, 2, 0, 0, bytes())
            elif type == FileTransferMessages.DirPacket:
                #rfbADrivesList
                if param == 3:
                    print(data.decode("latin-1"))

run(main())