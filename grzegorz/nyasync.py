import asyncio
from asyncio.streams import StreamReader, StreamWriter

def ify(func):
    """Decorate func to run async in default executor"""
    async def asyncified(*args, **kwargs):
        asyncloop = asyncio.get_event_loop()
        return await asyncloop.run_in_executor(
            None, lambda: func(*args, **kwargs))
    return asyncified

def safely(func, *args, **kwargs):
    asyncloop = asyncio.get_event_loop()
    asyncloop.call_soon_threadsafe(lambda: func(*args, **kwargs))

def callback(coro, callback=None):
    asyncloop = asyncio.get_event_loop()
    future = asyncio.run_cooroutine_threadsafe(coro, asyncloop)
    if callback:
        future.add_done_callback(callback)
    return future

def run(*coros):
    asyncloop = asyncio.get_event_loop()
    return asyncloop.run_until_complete(asyncio.gather(*coros))

class Queue(asyncio.Queue):
    __anext__ = asyncio.Queue.get

    def __aiter__(self):
        return self

class Event:
    def __init__(self):
        self.monitor = asyncio.Condition()

    def __aiter__(self):
        return self.monitor.wait()

    async def notify(self):
        with await self.monitor:
            self.monitor.notify_all()

class Condition:
    def __init__(self, predicate):
        self.predicate = predicate
        self.monitor = asyncio.Condition()

    def __aiter__(self):
        return self.monitor.wait_for(self.predicate)

    async def notify(self):
        with await self.monitor:
            self.monitor.notify_all()

class UnixConnection:
    def __init__(self, reader: StreamReader, writer: StreamWriter):
        self.reader: StreamReader = reader
        self.writer: StreamWriter = writer

    @classmethod
    async def from_path(cls, path):
        endpoints = await asyncio.open_unix_connection(path, limit=2**24) # default is 2**16
        return cls(*endpoints)

    def __aiter__(self):
        return self.reader.__aiter__() # readline

    def write(self, data):
        self.writer.write(data)
