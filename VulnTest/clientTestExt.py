from client import Client
import clientTests
import clientAuthBypassTests
from asyncio import sleep, run
from tabulate import tabulate

host = "127.0.0.1"
port = 5900

async def test(func, times = 5, sleepTime = 2):
    result = True
    client = Client()
    await client.connect(host, port)
    await client.intro()
    result = await client.security("12345678")
    if result == False:
        return
    await client.clientInit()
    w,h = await client.ServerInit()
    await func(client, w, h)
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
    #for t in clientTests.tests:
    for i in range(1):
        #name = t.__qualname__
        name = "1"
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