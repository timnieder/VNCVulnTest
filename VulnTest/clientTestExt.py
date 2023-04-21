from client import Client
import clientTestsExt
import clientAuthBypassTests
from asyncio import sleep, run
from tabulate import tabulate

host = "127.0.0.1"
port = 5900
w = 400
h = 300

async def test(func, times = 5, sleepTime = 2):
    result = True
    client = Client()
    await client.connect(host, port)
    await func(client)
    try:
        for i in range(times):
            if client.writer.is_closing():
                raise Exception("closing")
            print("tick")
            await client.framebufferUpdateRequest(False, 0, 0, w, h)
            # read image?
            await sleep(sleepTime)
    except Exception as e:
        print(f"Exception: {e}")
        result = False
    
    await client.disconnect()
    return result

async def main():
    print("Tests:")
    results = []
    for t in clientTestsExt.tests:
        name = t.__qualname__
        print(name)
        result = False
        try:
            result = await test(t)
        except Exception as e:
            print(f"Exception during test: {e}")
        results.append([name, result])
        await sleep(1)
    print(tabulate(results, headers=["Function", "Still running?"], tablefmt="grid"))

run(main())