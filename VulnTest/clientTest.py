from client import Client
import clientTests
import clientAuthBypassTests
from asyncio import sleep, run
from tabulate import tabulate

host = "localhost"
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
    w,h,format = await client.ServerInit()
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

async def authBypassTest(func, times = 5, sleepTime = 2):
    disconnected = False
    client = Client()
    w,h = 800,600
    try:
        w,h = await func(client)
        if client.writer.is_closing(): # check if its closed after our function
            raise Exception("closing after func")
    except Exception as e:
        print(f"Exception during func: {e}")
    
    try:
        for i in range(times): # request frame updates
            print("tick")
            await client.framebufferUpdateRequest(False, 0, 0, w, h)
            # read image?
            await sleep(sleepTime)
            if client.writer.is_closing():
                raise Exception("closing")
    except Exception as e:
        print(f"Exception: {e}")
        disconnected = True
    
    await client.disconnect()
    return disconnected

async def main():
    print("Tests:")
    results = []
    for t in clientTests.tests:
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

    print("Auth Bypass Tests")
    results = []
    for t in clientAuthBypassTests.authBypassTests:
        name = t.__qualname__
        print(name)
        result = True
        try:
            result = await authBypassTest(t)
        except Exception as e:
            print(f"Exception during auth bypass test: {e}")
        results.append([name, result])
        await sleep(1)
    print(tabulate(results, headers=["Function", "Disconnected"], tablefmt="grid"))

run(main())