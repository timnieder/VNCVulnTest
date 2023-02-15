from server import PixelFormat, Server
from asyncio import run, sleep, CancelledError
from tabulate import tabulate
import serverTests

async def test(func, w = 300, h = 300):
    width = w
    height = h
    format = PixelFormat(32, 32, False, True, 255, 255, 255, 16, 8, 0)
    server = Server(width, height, format)
    host = "127.0.0.1"
    port = 5900
    server.result = True
    async def callback(reader, writer):
        server.reader = reader
        server.writer = writer
        try:
            await func(server)
        except Exception as e:
            print(f"Exception: {e}")
            server.result = False
        await server.disconnect()
        server.server.close()
        await server.server.wait_closed()
    try:
        await server.listen(callback, host, port)
    except CancelledError:
        print(f"Canceled, result: {server.result}")
    return server.result

async def main():
    print("Tests:")
    results = []
    for t in serverTests.tests:
        name = t.__qualname__
        print(name)
        result = False
        try:
            result = await test(t)
        except Exception as e:
            print(f"Exception during test: {e}")
        except CancelledError:
            print("Canceled")
        results.append([name, result])
        await sleep(1)
    print(tabulate(results, headers=["Function", "Still running?"], tablefmt="grid"))

run(main())