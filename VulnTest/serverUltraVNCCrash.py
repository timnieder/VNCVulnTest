from asyncio import run, sleep, start_server, StreamReader, StreamWriter
import struct

def framebufferUpdate(num: int, rectangle, pixelData) -> bytes:
    msg = bytes()
    message_type = int(0)
    padding = int(0)
    msg += struct.pack(">BBH", message_type, padding, num)
    msg += struct.pack(">hhhhi",
        rectangle[0], # x
        rectangle[1], # y
        rectangle[2], # w
        rectangle[3], # h
        rectangle[4], # encoding-type
    ) + pixelData
    return msg

async def callback(reader: StreamReader, writer: StreamWriter):
    width = 2000
    height = 2000
    bpp = 32
    writer.write(b"RFB 003.008\n") # protocol handshake
    await reader.readline() # response
    writer.write(int(1).to_bytes(1, "big") + int(1).to_bytes(1, "big")) # 1 security type: NONE
    await reader.readexactly(1) # selected type
    writer.write(int(0).to_bytes(4, "big")) # security result
    await reader.readexactly(1) # client init, shared flag
    # server init
    writer.write(
            struct.pack(">HHBBBBHHHBBBBBBI",
                        width, height, # Framebuffer width and height
                        bpp, # Bits per pixel
                        32, # Color depth
                        0, # Big endian
                        1, # True Color
                        255, 255, 255, # Color max values
                        16, 8, 0, # Color shifts
                        0, 0, 0, # Padding
                        7, # Name length
            ) + ("desktop".encode("latin-1")) # Name
        )
    w = 30
    h = 1
    data = b'\x00'*w*h*int(bpp/4)
    y = height
    x = width
    print(f"x: {x}, y: {y}, len: {len(data)}")

    while True:
        writer.write(framebufferUpdate(1, (x, y, w, h, 0), data))
        print("tick")
        await sleep(5)

async def main():
    host = "127.0.0.1"
    port = 5900
    server = await start_server(callback, host, port)
    print(f"serving on {host}:{port}")
    async with server:
        await server.serve_forever()

run(main())