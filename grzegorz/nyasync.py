import asyncio

def ify(func):
    """Decorate func to run async in default executor"""
    asyncloop = asyncio.get_event_loop()
    async def asyncified(*args, **kwargs):
        return await asyncloop.run_in_executor(
            None, lambda: func(*args, **kwargs))
    return asyncified

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
    def __init__(self, path):
        (self.reader, self.writer) = await asyncio.open_unix_connection(path)

    def __aiter__(self):
        return self.reader.__aiter__()

    def write(self, data):
        return self.writer.write(data);
