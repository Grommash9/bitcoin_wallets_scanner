import asyncio
from threading import Timer


async def hello_world():
    await asyncio.sleep(3)
    print('Hello World!')


def wait():
    asyncio.run(hello_world())


timer = Timer(3, wait)
timer.start()
timer.join()