from server import PixelFormat, Server
from asyncio import run, sleep, CancelledError
import serverTests

async def main(w = 300, h = 300):
    width = w
    height = h
    format = PixelFormat(32, 24, False, True, 255, 255, 255, 16, 8, 0)
    server = Server(width, height, format)
    host = "127.0.0.1"
    port = 5900
    async def callback(reader, writer):
        server.reader = reader
        server.writer = writer
        try:
            await serverTests.rfc(server)
        except Exception as e:
            print(f"Exception: {e}")
        await server.disconnect()
        server.server.close()
        await server.server.wait_closed()
    while True:
        try:
            await server.listen(callback, host, port)
        except CancelledError:
            print("Cancelled")
        except Exception as e:
            print(f"Exception: {e}")

run(main(20, 20))