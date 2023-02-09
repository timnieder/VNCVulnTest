from server import PixelFormat, Server
from asyncio import run
import serverTests

async def test(func):
    width = 300
    height = 300
    format = PixelFormat(32, 32, False, True, 255, 255, 255, 16, 8, 0)
    server = Server(width, height, format)
    host = "127.0.0.1"
    port = 5900
    async def callback(reader, writer):
        try:
            await func(server, reader, writer)
        except Exception as e:
            print(f"Exception during test: {e}")
    await server.listen(callback, host, port)

# TODO: tests
run(test(serverTests.rfc))