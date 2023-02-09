from client import Client
from helper import read_int

host = "192.168.182.5"
port = 5900

async def authBypassNothing(client: Client):
    await client.connect(host, port)
    return 800,600

async def authBypassInit(client: Client):
    await client.connect(host, port)
    await client.clientInit()
    return await client.ServerInit()

async def authBypassIntro(client: Client):
    await client.connect(host, port)
    await client.intro()
    return 800,600

async def authBypassIntroInit(client: Client):
    await client.connect(host, port)
    await client.intro()
    await client.clientInit()
    return await client.ServerInit()

async def authBypassHalfSecurity(client: Client):
    await client.connect(host, port)
    await client.intro()
    # only the first part of the handshake
    numberOfTypes = await read_int(client.reader, 1)
    auth_types = set(await client.reader.readexactly(numberOfTypes))
    auth_type = int(2)
    client.writer.write(auth_type.to_bytes(1, 'big'))
    await client.clientInit()
    return await client.ServerInit()

authBypassTests = [
    authBypassNothing,
    authBypassInit,
    authBypassIntro,
    authBypassIntroInit,
    authBypassHalfSecurity
]